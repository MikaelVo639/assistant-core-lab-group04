import re
from collections.abc import Collection

from assistant_core.models import Intent

GREETINGS = {"hi", "hello", "hey", "xin chao", "chao"}
GREETING_PREFIXES = ("hi ", "hello ", "hey ", "xin chao ", "chao ")

RULE_KEYWORDS = (
    "thesis",
    "exam",
    "gpa",
    "retake",
    "absence",
    "rule",
    "rules",
    "handbook",
    "regulation",
    "regulations",
    "register",
    "degree",
    "khóa luận",
    "khoa luan",
    "quy định",
    "quy dinh",
    "sổ tay",
    "so tay",
)


def route(text: str, office_names: Collection[str] = ()) -> Intent:
    m = text.lower().strip()
    if not m:
        return Intent.UNKNOWN

    cleaned = re.sub(r"[?!.,;:]", "", m)
    if cleaned in GREETINGS or m.startswith(GREETING_PREFIXES):
        return Intent.GREETING

    if "fee" in m or "tuition" in m or "học phí" in m or "hoc phi" in m:
        return Intent.FEE

    for name in office_names:
        if name.lower() in m:
            return Intent.OFFICE

    if any(keyword in m for keyword in RULE_KEYWORDS):
        return Intent.RULE

    return Intent.UNKNOWN
