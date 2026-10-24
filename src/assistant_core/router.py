import re
from collections.abc import Collection

from assistant_core.models import Intent

GREETINGS = frozenset({"hi", "hello", "hey", "xin chao", "chao"})
GREETING_PREFIXES = ("hi ", "hello ", "hey ", "xin chao ", "chao ")
HELP_REQUESTS = frozenset({"help", "what can you do", "what can you help with", "how can you help me"})

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
    """Prioritise concrete requests over a conversational greeting prefix."""
    m = text.lower().strip()
    if not m:
        return Intent.UNKNOWN

    cleaned = re.sub(r"[?!.,;:]", "", m)
    if _is_help_request(cleaned):
        return Intent.HELP
    if cleaned in GREETINGS:
        return Intent.GREETING

    if "fee" in m or "tuition" in m or "học phí" in m or "hoc phi" in m:
        return Intent.FEE

    for name in office_names:
        if name.lower() in m:
            return Intent.OFFICE

    if any(keyword in m for keyword in RULE_KEYWORDS):
        return Intent.RULE

    if m.startswith(GREETING_PREFIXES):
        return Intent.GREETING
    return Intent.UNKNOWN


def _is_help_request(cleaned: str) -> bool:
    """Match complete help requests without shadowing office names or domain questions."""
    request = " ".join(cleaned.split())
    for prefix in GREETING_PREFIXES:
        if request.startswith(prefix):
            request = request[len(prefix) :].strip()
            break
    return request in HELP_REQUESTS
