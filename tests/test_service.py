"""Exercise service orchestration against the documented collaborator contracts."""

import importlib
import logging
import sys

import pytest


def test_component_fixture_restores_package_import_state():
    """A later import must not reuse a service modified for an earlier test."""
    from component_fixtures import collaborator_scope

    package = importlib.import_module("assistant_core")
    missing = object()
    names = ("service", "__main__")
    old_attributes = {name: package.__dict__.get(name, missing) for name in names}
    old_modules = {name: sys.modules.get(f"assistant_core.{name}", missing) for name in names}
    with collaborator_scope():
        for name in names:
            importlib.import_module(f"assistant_core.{name}")
    for name in names:
        assert package.__dict__.get(name, missing) is old_attributes[name]
        assert sys.modules.get(f"assistant_core.{name}", missing) is old_modules[name]


@pytest.fixture
def service_module(core_contracts, monkeypatch):
    module = importlib.import_module("assistant_core.service")
    # Select the flow under test explicitly; real router behavior is checked separately.
    monkeypatch.setattr(module, "route", lambda text, names: core_contracts.models.Intent.RULE)
    return module


@pytest.fixture
def service(service_module, core_contracts):
    c = core_contracts
    return service_module.AssistantService(c.settings, c.offices, c.handbook, c.responder.StubLLMResponder())


def test_greeting_does_not_query_knowledge(service, service_module, core_contracts, monkeypatch):
    c = core_contracts
    monkeypatch.setattr(service_module, "route", lambda text, names: c.models.Intent.GREETING)

    def unexpected_search(text):
        pytest.fail("A greeting must not query the handbook")

    monkeypatch.setattr(c.handbook, "search", unexpected_search)
    result = service.handle(c.models.Message(text="hello"))
    assert result.intent is c.models.Intent.GREETING
    assert "offices, fees and rules" in result.answer
    assert result.sources == [] and not result.degraded


def test_fee_uses_parsed_credits_and_configured_rates(service, service_module, core_contracts, monkeypatch):
    c = core_contracts
    c.settings.credit_rate_vnd = 500_000
    c.settings.retake_multiplier = 2.0
    c.settings.max_credits = 25
    monkeypatch.setattr(service_module, "route", lambda text, names: c.models.Intent.FEE)

    def parse(text):
        assert text == "tuition for 18 credits and 2 retake"
        return 18, 2

    def calculate(credits, retake, rate, multiplier, maximum):
        assert (credits, retake, rate, multiplier, maximum) == (18, 2, 500_000, 2.0, 25)
        return 11_000_000

    monkeypatch.setattr(service_module, "parse_credits", parse)
    monkeypatch.setattr(service_module, "tuition", calculate)
    result = service.handle(c.models.Message(text="tuition for 18 credits and 2 retake"))
    assert result.answer == "Your tuition is 11,000,000 VND."
    assert result.intent is c.models.Intent.FEE


@pytest.mark.parametrize("failure_at", ["parse", "tuition"])
def test_invalid_credit_request_returns_a_useful_fee_response(
    service, service_module, core_contracts, monkeypatch, failure_at
):
    c = core_contracts
    monkeypatch.setattr(service_module, "route", lambda text, names: c.models.Intent.FEE)

    def reject(*args):
        raise c.errors.InvalidRequest("Credits must be between 1 and 30.")

    monkeypatch.setattr(service_module, "parse_credits", reject if failure_at == "parse" else lambda text: (31, 0))
    monkeypatch.setattr(service_module, "tuition", reject)
    result = service.handle(c.models.Message(text="tuition 31 credits"))
    assert result.intent is c.models.Intent.FEE
    assert result.answer == "Credits must be between 1 and 30."
    assert not result.degraded


def test_office_answer_uses_directory_values(service, service_module, core_contracts, monkeypatch):
    c = core_contracts

    def office_route(text, names):
        assert text == "where is the library" and names == {"library"}
        return c.models.Intent.OFFICE

    monkeypatch.setattr(service_module, "route", office_route)
    result = service.handle(c.models.Message(text="where is the library"))
    assert result.answer == "Library: room B.201, open Mon-Sat 07:00-20:00."
    assert result.intent is c.models.Intent.OFFICE


def test_missing_office_is_unknown(service, service_module, core_contracts, monkeypatch):
    c = core_contracts
    monkeypatch.setattr(service_module, "route", lambda text, names: c.models.Intent.OFFICE)
    monkeypatch.setattr(c.offices, "find", lambda text: None)
    result = service.handle(c.models.Message(text="library"))
    assert result.intent is c.models.Intent.UNKNOWN
    assert result.sources == [] and not result.degraded


def test_rule_answer_preserves_its_source(service, core_contracts):
    c = core_contracts
    result = service.handle(c.models.Message(text="thesis registration credits"))
    assert result.intent is c.models.Intent.RULE
    assert "Thesis registration" in result.answer
    assert [(source.id, source.title) for source in result.sources] == [("H26-5.3", "Thesis registration")]
    assert not result.degraded


def test_missing_rule_is_unknown_without_calling_provider(service, core_contracts, monkeypatch):
    c = core_contracts
    monkeypatch.setattr(c.handbook, "search", lambda text: None)

    def unexpected_provider(question, rule):
        pytest.fail("A missing rule must not call the provider")

    monkeypatch.setattr(service.responder, "explain", unexpected_provider)
    result = service.handle(c.models.Message(text="weather tomorrow"))
    assert result.intent is c.models.Intent.UNKNOWN
    assert result.answer and result.sources == []


def test_provider_failure_uses_template_and_keeps_source(service, core_contracts, monkeypatch, caplog):
    c = core_contracts

    def fail(question, rule):
        raise c.errors.ProviderError("api-key-private provider payload")

    monkeypatch.setattr(service.responder, "explain", fail)
    with caplog.at_level(logging.INFO, logger="assistant_core"):
        result = service.handle(
            c.models.Message(text="thesis registration private full user question", session_id="session-7")
        )
    assert result.answer.startswith("Thesis registration: Students may register")
    assert result.degraded
    assert [source.id for source in result.sources] == ["H26-5.3"]
    assert "fallback" in caplog.text
    assert "api-key-private" not in caplog.text and "private full user question" not in caplog.text
    handled = [record for record in caplog.records if record.getMessage() == "handled"]
    assert len(handled) == 1
    record = handled[0]
    assert record.intent == "rule" and record.degraded is True and record.session == "session-7"
    assert isinstance(record.latency_ms, int | float) and record.latency_ms >= 0


def test_unexpected_provider_errors_are_not_hidden(service, core_contracts, monkeypatch):
    def fail(question, rule):
        raise RuntimeError("programming defect")

    monkeypatch.setattr(service.responder, "explain", fail)
    with pytest.raises(RuntimeError, match="programming defect"):
        service.handle(core_contracts.models.Message(text="thesis registration"))


def test_normal_response_logs_metadata_without_question_or_settings(service, core_contracts, caplog):
    c = core_contracts
    c.settings.llm_api_key = "private-config-key"
    with caplog.at_level(logging.INFO, logger="assistant_core"):
        service.handle(c.models.Message(text="thesis registration the entire private question", session_id="local"))
    records = [record for record in caplog.records if record.getMessage() == "handled"]
    assert len(records) == 1 and records[0].degraded is False
    assert records[0].intent == "rule"
    assert "the entire private question" not in caplog.text and "private-config-key" not in caplog.text
