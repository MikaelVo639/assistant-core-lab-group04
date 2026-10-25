"""Tests for the responder boundary and structured JSON logging."""

from __future__ import annotations

import json
import logging
from collections.abc import Iterator

import pytest

from assistant_core.config import Settings
from assistant_core.errors import ProviderError
from assistant_core.knowledge import Rule
from assistant_core.logging_setup import HANDLER_NAME, LOGGER_NAME, setup_logging
from assistant_core.responder import Responder, StubLLMResponder, TemplateResponder, make_responder

RULE = Rule(
    id="H26-5.3",
    title="Thesis registration",
    text="Students may register a thesis when they have at least 120 accumulated credits.",
)


@pytest.fixture(autouse=True)
def _restore_logger() -> Iterator[None]:
    logger = logging.getLogger(LOGGER_NAME)
    saved_handlers = logger.handlers[:]
    saved_level = logger.level
    saved_propagate = logger.propagate
    yield
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
        if handler.name == HANDLER_NAME:
            handler.close()
    for handler in saved_handlers:
        logger.addHandler(handler)
    logger.setLevel(saved_level)
    logger.propagate = saved_propagate


def test_template_responder_returns_title_and_handbook_text() -> None:
    assert TemplateResponder().explain("thesis?", RULE) == f"{RULE.title}: {RULE.text}"


def test_stub_responder_is_deterministic() -> None:
    responder = StubLLMResponder()

    first = responder.explain("thesis?", RULE)
    second = responder.explain("thesis?", RULE)

    assert first == second
    assert first == f"Based on '{RULE.title}': {RULE.text}"


def test_stub_responder_can_simulate_outage() -> None:
    with pytest.raises(ProviderError, match="stub provider unavailable"):
        StubLLMResponder(fail=True).explain("thesis?", RULE)


def test_responders_satisfy_protocol() -> None:
    assert isinstance(TemplateResponder(), Responder)
    assert isinstance(StubLLMResponder(), Responder)


def test_factory_selects_configured_responder() -> None:
    assert isinstance(make_responder(Settings(llm_provider="stub")), StubLLMResponder)
    assert isinstance(make_responder(Settings(llm_provider="template")), TemplateResponder)


def test_setup_logging_writes_one_json_line_with_approved_fields(capsys: pytest.CaptureFixture[str]) -> None:
    setup_logging("INFO")
    logging.getLogger(LOGGER_NAME).info(
        "handled",
        extra={
            "intent": "fee",
            "latency_ms": 1.25,
            "session": "local",
            "degraded": False,
            "api_key": "sk-secret-value",
            "text": "private user question",
        },
    )

    stderr = capsys.readouterr().err
    payload = json.loads(stderr.strip())

    assert payload == {
        "level": "INFO",
        "logger": LOGGER_NAME,
        "msg": "handled",
        "intent": "fee",
        "latency_ms": 1.25,
        "session": "local",
        "degraded": False,
    }
    assert "sk-secret-value" not in stderr
    assert "private user question" not in stderr


def test_setup_logging_is_idempotent_and_keeps_foreign_handlers() -> None:
    logger = logging.getLogger(LOGGER_NAME)
    unrelated = logging.NullHandler()
    logger.addHandler(unrelated)

    setup_logging("INFO")
    setup_logging("DEBUG")

    owned = [handler for handler in logger.handlers if handler.name == HANDLER_NAME]
    assert len(owned) == 1
    assert unrelated in logger.handlers
    assert logger.level == logging.DEBUG


def test_logging_does_not_include_exception_details(capsys: pytest.CaptureFixture[str]) -> None:
    setup_logging("INFO")
    logger = logging.getLogger(LOGGER_NAME)
    try:
        raise RuntimeError("secret exception detail")
    except RuntimeError:
        logger.exception("provider failed")

    stderr = capsys.readouterr().err
    payload = json.loads(stderr.strip())

    assert payload["msg"] == "provider failed"
    assert "exception" not in payload
    assert "secret exception detail" not in stderr
