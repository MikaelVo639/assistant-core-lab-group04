"""Tests for deterministic responders and safe structured logging."""

import json
import logging

import pytest

from assistant_core.errors import ProviderError
from assistant_core.knowledge import Rule
from assistant_core.logging_setup import HANDLER_NAME, setup_logging
from assistant_core.responder import StubLLMResponder, TemplateResponder

RULE = Rule(
    id="H26-7.2",
    title="Exam absence",
    text="Students must submit medical evidence within 3 working days.",
)


def test_template_responder_uses_the_retrieved_rule() -> None:
    answer = TemplateResponder().explain("What happens if I miss an exam?", RULE)

    assert answer == "Exam absence: Students must submit medical evidence within 3 working days."


def test_stub_responder_is_deterministic() -> None:
    responder = StubLLMResponder()

    first = responder.explain("What happens if I miss an exam?", RULE)
    second = responder.explain("What happens if I miss an exam?", RULE)

    assert first == second
    assert first == "Based on 'Exam absence': Students must submit medical evidence within 3 working days."


def test_stub_responder_can_simulate_a_provider_failure() -> None:
    with pytest.raises(ProviderError, match="stub provider unavailable"):
        StubLLMResponder(fail=True).explain("What happens if I miss an exam?", RULE)


def test_logging_is_idempotent_json_only_and_uses_stderr(capsys: pytest.CaptureFixture[str]) -> None:
    logger = logging.getLogger("assistant_core")
    original_handlers = logger.handlers[:]
    original_level = logger.level
    original_propagate = logger.propagate
    unrelated_handler = logging.NullHandler()
    logger.addHandler(unrelated_handler)

    try:
        setup_logging("info")
        setup_logging("INFO")

        owned_handlers = [handler for handler in logger.handlers if handler.name == HANDLER_NAME]
        assert len(owned_handlers) == 1
        assert unrelated_handler in logger.handlers

        logger.info(
            "handled",
            extra={
                "intent": "rule",
                "latency_ms": 0.125,
                "session": "local",
                "degraded": False,
                "question": "private full user message",
                "api_key": "private-api-key",
            },
        )

        output = capsys.readouterr()
        records = [json.loads(line) for line in output.err.splitlines()]

        assert output.out == ""
        assert len(records) == 1
        assert records[0] == {
            "level": "INFO",
            "logger": "assistant_core",
            "msg": "handled",
            "intent": "rule",
            "latency_ms": 0.125,
            "session": "local",
            "degraded": False,
        }
        assert "private full user message" not in output.err
        assert "private-api-key" not in output.err
    finally:
        for handler in logger.handlers[:]:
            if handler not in original_handlers:
                logger.removeHandler(handler)
                handler.close()
        logger.handlers = original_handlers
        logger.setLevel(original_level)
        logger.propagate = original_propagate
