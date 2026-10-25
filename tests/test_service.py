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
