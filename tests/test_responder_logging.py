"""Check deterministic responders and real JSON logging on stderr."""

import importlib
import json
import logging
from types import SimpleNamespace

import pytest

from assistant_core.errors import ProviderError


def test_stub_is_deterministic_and_can_fail_by_request():
    responder = importlib.import_module("assistant_core.responder")
    rule = SimpleNamespace(id="r1", title="Exam absence", text="Submit evidence within 3 working days.")
    stub = responder.StubLLMResponder()
    assert stub.explain("absence", rule) == stub.explain("absence", rule)
    assert "3 working days" in responder.TemplateResponder().explain("absence", rule)
    with pytest.raises(ProviderError):
        responder.StubLLMResponder(fail=True).explain("absence", rule)


def test_setup_is_idempotent_and_only_writes_json_to_stderr(capsys):
    setup = importlib.import_module("assistant_core.logging_setup").setup_logging
    logger = logging.getLogger("assistant_core")
    old_handlers, old_level, old_propagate = logger.handlers[:], logger.level, logger.propagate
    try:
        setup("INFO")
        setup("INFO")
        logger.info("handled", extra={"intent": "fee", "latency_ms": 0.2, "session": "local", "degraded": False})
        output = capsys.readouterr()
        records = [json.loads(line) for line in output.err.splitlines()]
        assert output.out == "" and len(records) == 1
        assert records[0]["intent"] == "fee" and records[0]["degraded"] is False
    finally:
        for handler in logger.handlers[:]:
            if handler not in old_handlers:
                logger.removeHandler(handler)
                handler.close()
        logger.handlers = old_handlers
        logger.setLevel(old_level)
        logger.propagate = old_propagate
