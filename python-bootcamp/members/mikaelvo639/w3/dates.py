"""Parse the small set of due-date expressions required by W3-1."""

import re
from datetime import date, timedelta

_WEEKDAYS = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")


def parse_due(text: str, today: date) -> date:
    """Parse ISO dates, tomorrow, nonnegative day offsets or English weekdays.

    Weekdays accept full names or three-letter abbreviations, ignoring case
    and surrounding whitespace. The same weekday as today means next week.
    Unsupported expressions and invalid calendar dates raise ValueError.
    """
    normalized = text.strip().lower()
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", normalized):
        return date.fromisoformat(normalized)
    if normalized == "tomorrow":
        return today + timedelta(days=1)
    offset = re.fullmatch(r"in (\d+) days?", normalized)
    if offset:
        return today + timedelta(days=int(offset.group(1)))
    for index, weekday in enumerate(_WEEKDAYS):
        if normalized in (weekday, weekday[:3]):
            return today + timedelta(days=(index - today.weekday()) % 7 or 7)
    raise ValueError(f"Unknown due date: {text!r}")
