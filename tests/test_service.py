"""Offline integration tests for the orchestrated service."""

from __future__ import annotations

from pathlib import Path

import pytest

from assistant_core.config import Settings
from assistant_core.knowledge import Handbook, OfficeDirectory
from assistant_core.models import Intent, Message
from assistant_core.responder import StubLLMResponder
from assistant_core.service import AssistantService

DATA = Path(__file__).resolve().parents[1] / "data"


def make(fail: bool = False) -> AssistantService:
    return AssistantService(Settings(), OfficeDirectory(DATA), Handbook(DATA), StubLLMResponder(fail=fail))


def ask(svc: AssistantService, text: str):
    return svc.handle(Message(text=text))


def test_greeting():
    assert ask(make(), "hi").intent is Intent.GREETING


def test_fee():
    assert ask(make(), "tuition for 18 credits and 2 retake").answer == "Your tuition is 9450000 VND"


def test_fee_too_many_credits():
    assert ask(make(), "tuition 40 credits").answer == "too many credits"


def test_office():
    r = ask(make(), "where is the training office")
    assert r.intent is Intent.OFFICE and "room I.101" in r.answer


def test_rule_with_source():
    r = ask(make(), "can I register my thesis with 118 credits")
    assert r.intent is Intent.RULE and r.sources and not r.degraded


def test_provider_failure_degrades_but_keeps_source():
    r = ask(make(fail=True), "can I register my thesis with 118 credits")
    assert r.degraded and r.sources and "(source: " in r.answer


def test_unknown():
    assert ask(make(), "zzz").intent is Intent.UNKNOWN


def test_empty_message_rejected():
    with pytest.raises(ValueError):
        Message(text="")
from assistant_core.service import AssistantService, build_service

DATA_DIR = Path(__file__).resolve().parents[1] / "data"
THESIS_TEXT = (
    "Students may register a thesis when they have at least 120 accumulated credits " "and a GPA of at least 2.0."
)


@pytest.fixture
def settings() -> Settings:
    return Settings(data_dir=DATA_DIR)


@pytest.fixture
def service(settings: Settings) -> AssistantService:
    return AssistantService(
        settings,
        OfficeDirectory.from_csv(DATA_DIR),
        Handbook.from_json(DATA_DIR),
        StubLLMResponder(),
    )


@pytest.fixture
def failing_service(settings: Settings) -> AssistantService:
    return AssistantService(
        settings,
        OfficeDirectory.from_csv(DATA_DIR),
        Handbook.from_json(DATA_DIR),
        StubLLMResponder(fail=True),
    )


@pytest.mark.parametrize("text", ["hi", "hello", "xin chao"])
def test_greeting(service: AssistantService, text: str) -> None:
    response = service.handle(Message(text=text))

    assert response.answer == "Hello! I can help with offices, fees and rules."
    assert response.intent is Intent.GREETING
    assert response.sources == []
    assert response.degraded is False


def test_tuition_with_retake(service: AssistantService) -> None:
    response = service.handle(Message(text="tuition for 18 credits and 2 retake"))

    assert response.answer == "Your tuition is 9450000 VND"
    assert response.intent is Intent.FEE


def test_tuition_uses_injected_settings(settings: Settings) -> None:
    custom = settings.model_copy(update={"credit_rate_vnd": 500_000, "retake_multiplier": 2.0, "max_credits": 20})
    service = AssistantService(
        custom,
        OfficeDirectory.from_csv(DATA_DIR),
        Handbook.from_json(DATA_DIR),
        StubLLMResponder(),
    )

    response = service.handle(Message(text="tuition for 10 credits and 2 retake"))

    assert response.answer == "Your tuition is 7000000 VND"


def test_too_many_credits(service: AssistantService) -> None:
    response = service.handle(Message(text="tuition 40 credits"))

    assert response.answer == "too many credits"
    assert response.intent is Intent.FEE


def test_missing_credit_count(service: AssistantService) -> None:
    response = service.handle(Message(text="what is the tuition fee?"))

    assert response.answer == "How many credits?"
    assert response.intent is Intent.FEE


def test_office_lookup(service: AssistantService) -> None:
    response = service.handle(Message(text="where is the library"))

    assert response.answer == "Library: room B.201, open Mon-Sat 07:00-20:00"
    assert response.intent is Intent.OFFICE


def test_rule_answer_has_source(service: AssistantService) -> None:
    response = service.handle(Message(text="can I register my thesis with 118 credits"))

    assert response.answer == f"Based on 'Thesis registration': {THESIS_TEXT} (source: H26-5.3)"
    assert response.intent is Intent.RULE
    assert response.degraded is False
    assert [(source.id, source.title) for source in response.sources] == [("H26-5.3", "Thesis registration")]


def test_provider_failure_uses_template_and_keeps_source(failing_service: AssistantService) -> None:
    response = failing_service.handle(Message(text="can I register my thesis with 118 credits"))

    assert response.answer == f"{THESIS_TEXT} (source: H26-5.3)"
    assert response.intent is Intent.RULE
    assert response.degraded is True
    assert [source.id for source in response.sources] == ["H26-5.3"]


def test_unknown_question(service: AssistantService) -> None:
    response = service.handle(Message(text="weather tomorrow"))

    assert response.answer == "Sorry I dont know"
    assert response.intent is Intent.UNKNOWN
    assert response.sources == []


def test_build_service_loads_packaged_data(settings: Settings) -> None:
    service = build_service(settings)

    response = service.handle(Message(text="where is the library"))

    assert response.answer == "Library: room B.201, open Mon-Sat 07:00-20:00"
