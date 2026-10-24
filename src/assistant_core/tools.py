import re

from assistant_core.errors import InvalidRequest


def parse_credits(text: str) -> tuple[int, int]:
    cleaned = re.sub(r"[?,.:;!]", " ", text.lower())
    words = cleaned.split()

    credits = 0
    retake = 0

    retake_match = re.search(r"(\d+)\s*(?:retake|học lại|hoc lai)", cleaned)
    if retake_match:
        retake = int(retake_match.group(1))

    credit_match = re.search(r"(\d+)\s*(?:credit|tín chỉ|tin chi|tc)", cleaned)
    if credit_match:
        credits = int(credit_match.group(1))

    if credits == 0 and retake == 0:
        for i, word in enumerate(words):
            if word.isdigit():
                if i + 1 < len(words) and words[i + 1].startswith("retake"):
                    retake = int(word)
                elif credits == 0:
                    credits = int(word)

    if credits == 0 and retake > 0:
        credits = retake

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

    total = credits * rate + retake * rate * retake_multiplier
    return int(round(total))
