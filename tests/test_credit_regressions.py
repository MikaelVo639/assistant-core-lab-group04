"""Protect real integration from silent changes to credit counts and intent priority."""

import pytest

from assistant_core.errors import InvalidRequest
from assistant_core.models import Intent
from assistant_core.router import route
from assistant_core.tools import parse_credits


@pytest.mark.parametrize(
    "question",
    [
        "tuition -5 credits",
        "tuition 1.5 credits",
        "tuition for 18 credits and -2 retake",
        "tuition 18.5 credits",
        "tuition 0 credits and 2 retake",
        "tuition 2 retake",
        "tuition .5 credits",
        "tuition -.5 credits",
        "tuition 18 credits and .5 retakes",
    ],
)
def test_invalid_counts_are_not_reinterpreted_as_chargeable_positive_credits(question):
    with pytest.raises(InvalidRequest):
        parse_credits(question)


@pytest.mark.parametrize(
    "question,intent",
    [
        ("hi tuition for 18 credits", Intent.FEE),
        ("hello where is the library", Intent.OFFICE),
        ("hey thesis registration credits", Intent.RULE),
    ],
)
def test_a_greeting_prefix_does_not_hide_the_actual_request(question, intent):
    assert route(question, {"library"}) is intent


def test_oversized_retake_counts_produce_a_named_error_instead_of_a_crash():
    from assistant_core.tools import tuition

    question = "tuition 1 credits and " + "9" * 310 + " retakes"
    with pytest.raises(InvalidRequest):
        tuition(*parse_credits(question))
