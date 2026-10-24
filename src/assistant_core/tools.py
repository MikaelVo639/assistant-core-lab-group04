import re
from math import isfinite

from assistant_core.errors import InvalidRequest


def parse_credits(text: str) -> tuple[int, int]:
    """Extract positive normal credits and separate non-negative integer retakes."""
    if re.search(r"(?<!\w)[-\u2212]\s*\d|\d*[.,]\d", text):
        raise InvalidRequest("Credits must be non-negative whole numbers.")
    cleaned = re.sub(r"[?,.:;!]", " ", text.lower())
    retake_match = re.search(r"(\d+)\s*(?:retakes?|học lại|hoc lai)\b", cleaned)
    credit_match = re.search(r"(\d+)\s*(?:credits?|tín chỉ|tin chi|tc)\b", cleaned)
    retake = int(retake_match.group(1)) if retake_match else 0
    if credit_match is not None:
        credits = int(credit_match.group(1))
    else:
        normal_text = (
            cleaned if retake_match is None else cleaned[: retake_match.start()] + cleaned[retake_match.end() :]
        )
        number = re.search(r"\b\d+\b", normal_text)
        credits = int(number.group()) if number else 0
    if credits <= 0:
        raise InvalidRequest("How many credits?")
    return credits, retake


def tuition(
    credits: int,
    retake: int = 0,
    rate: int = 450_000,
    retake_multiplier: float = 1.5,
    max_credits: int = 30,
) -> int:
    """Calculate the exact integer VND total without I/O or provider calls."""
    if credits <= 0:
        raise InvalidRequest("How many credits?")
    if credits > max_credits:
        raise InvalidRequest("too many credits")
    if retake < 0:
        raise InvalidRequest("retake credits must be non-negative")
    if rate <= 0:
        raise InvalidRequest("credit rate must be positive")
    if retake_multiplier < 0:
        raise InvalidRequest("retake multiplier must be non-negative")

    try:
        total = credits * rate + retake * rate * retake_multiplier
        if not isfinite(total):
            raise InvalidRequest("Tuition values are outside the supported numeric range.")
        return int(round(total))
    except (OverflowError, ValueError):
        raise InvalidRequest("Tuition values are outside the supported numeric range.") from None
