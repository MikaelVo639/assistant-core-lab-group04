"""Record the original behaviour; these are not tests of the future service."""

from types import ModuleType

import pytest


@pytest.mark.parametrize("text", ["hi", "xin chao"])
def test_greeting(monolith: ModuleType, text: str) -> None:
    assert monolith.handle(text) == "Hello! I can help with offices, fees and rules."


def test_tuition_with_retake(monolith: ModuleType) -> None:
    assert monolith.handle("tuition for 18 credits and 2 retake") == "Your tuition is 9450000 VND"


def test_office_lookup(monolith: ModuleType) -> None:
    assert monolith.handle("where is the library") == "Library: room B.201, open Mon-Sat 07:00-20:00"


def test_too_many_credits(monolith: ModuleType) -> None:
    assert monolith.handle("tuition 40 credits") == "too many credits"


def test_empty_message(monolith: ModuleType) -> None:
    assert monolith.handle("") == "empty"


def test_unknown_question(monolith: ModuleType) -> None:
    assert monolith.handle("weather tomorrow") == "Sorry I dont know"


def test_rule_answer_has_source(monolith: ModuleType, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(monolith, "llm", lambda _prompt: "Answer from deterministic stub")
    answer = monolith.handle("can I register my thesis with 118 credits")
    assert answer == "Answer from deterministic stub (source: H26-5.3)"


def test_rule_fallback_keeps_source(monolith: ModuleType, monkeypatch: pytest.MonkeyPatch) -> None:
    def fail_provider(_prompt: str) -> str:
        raise RuntimeError("simulated provider failure")

    monkeypatch.setattr(monolith, "llm", fail_provider)
    answer = monolith.handle("can I register my thesis with 118 credits")
    assert answer == (
        "Students may register a thesis when they have at least 120 accumulated credits "
        "and a GPA of at least 2.0. (source: H26-5.3)"
    )
