"""Boundary tests for the public request and response models."""

import pytest
from pydantic import ValidationError

from assistant_core.models import Intent, Message, Response, Source


def test_message_trims_text_and_defaults_session() -> None:
    message = Message(text="  where is the library  ")

    assert message.text == "where is the library"
    assert message.session_id == "local"


@pytest.mark.parametrize("text", ["", "   ", "\n\t"])
def test_message_rejects_blank_text(text: str) -> None:
    with pytest.raises(ValidationError):
        Message(text=text)


def test_message_rejects_text_longer_than_2000_characters() -> None:
    with pytest.raises(ValidationError):
        Message(text="x" * 2001)


def test_response_defaults_are_independent_lists() -> None:
    first = Response(answer="a", intent=Intent.UNKNOWN)
    second = Response(answer="b", intent=Intent.UNKNOWN)

    assert first.sources == []
    assert second.sources == []
    assert first.degraded is False


def test_source_serialises_expected_fields() -> None:
    source = Source(id="H26-5.3", title="Thesis registration")

    assert source.model_dump() == {"id": "H26-5.3", "title": "Thesis registration"}


def test_message_accepts_both_length_boundaries() -> None:
    assert Message(text="x").text == "x"
    assert len(Message(text="x" * 2000).text) == 2000


@pytest.mark.parametrize("text", [None, 123, ["hello"]])
def test_message_rejects_non_string_text(text: object) -> None:
    with pytest.raises(ValidationError):
        Message(text=text)  # type: ignore[arg-type]


def test_message_keeps_explicit_session_id() -> None:
    assert Message(text="hello", session_id="student-42").session_id == "student-42"


def test_intent_values_are_stable_strings() -> None:
    assert {intent.value for intent in Intent} == {
        "greeting",
        "fee",
        "office",
        "rule",
        "unknown",
    }
    assert Intent.FEE == "fee"


def test_response_requires_a_known_intent() -> None:
    with pytest.raises(ValidationError):
        Response(answer="hello", intent="not-an-intent")  # type: ignore[arg-type]


def test_response_serialises_sources_and_degraded_state() -> None:
    response = Response(
        answer="Thesis rule (source: H26-5.3)",
        intent=Intent.RULE,
        sources=[Source(id="H26-5.3", title="Thesis registration")],
        degraded=True,
    )

    assert response.model_dump() == {
        "answer": "Thesis rule (source: H26-5.3)",
        "intent": Intent.RULE,
        "sources": [{"id": "H26-5.3", "title": "Thesis registration"}],
        "degraded": True,
    }


@pytest.mark.parametrize("payload", [{"title": "Thesis registration"}, {"id": "H26-5.3"}])
def test_source_requires_id_and_title(payload: dict[str, str]) -> None:
    with pytest.raises(ValidationError):
        Source(**payload)
