import pytest

from assistant_core.models import Intent
from assistant_core.router import route

OFFICES = {"library", "student affairs", "it helpdesk"}


@pytest.mark.parametrize("text", ["hi", "hello", "hey", "xin chao", "Hello!", "hi there", "Xin chao!"])
def test_route_greeting(text):
    assert route(text, OFFICES) is Intent.GREETING


@pytest.mark.parametrize(
    "text",
    [
        "tuition for 18 credits",
        "how much is tuition?",
        "what is the fee",
        "học phí học kỳ 1",
        "fee for 20 credits and 2 retake",
    ],
)
def test_route_fee(text):
    assert route(text, OFFICES) is Intent.FEE


def test_route_office():
    assert route("where is the library", OFFICES) is Intent.OFFICE
    assert route("student affairs room and hours", OFFICES) is Intent.OFFICE
    assert route("contact IT Helpdesk", OFFICES) is Intent.OFFICE


def test_route_unlisted_office_is_not_office():
    assert route("where is the gym", OFFICES) is Intent.UNKNOWN


@pytest.mark.parametrize(
    "text",
    [
        "can I register my thesis with 118 credits",
        "what is the exam absence policy",
        "minimum gpa required",
        "handbook regulations for graduation",
        "quy định xét tốt nghiệp",
    ],
)
def test_route_rule(text):
    assert route(text, OFFICES) is Intent.RULE


@pytest.mark.parametrize("text", ["", "   ", "weather tomorrow", "tell me a joke", "random query 12345"])
def test_route_unknown(text):
    assert route(text, OFFICES) is Intent.UNKNOWN


def test_route_default_empty_offices():
    assert route("where is the library") is Intent.UNKNOWN
