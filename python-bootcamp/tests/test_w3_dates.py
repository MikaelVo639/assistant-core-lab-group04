"""Additional behavior checks for Minh W3-1 dates."""

from datetime import date

import pytest


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("2026-10-30", date(2026, 10, 30)),
        ("tomorrow", date(2026, 10, 27)),
        ("in 3 days", date(2026, 10, 29)),
        ("in 0 days", date(2026, 10, 26)),
        ("in 1 day", date(2026, 10, 27)),
        ("Fri", date(2026, 10, 30)),
        ("Monday", date(2026, 11, 2)),
        (" sun ", date(2026, 11, 1)),
    ],
)
def test_parse_due_supported_forms(text: str, expected: date) -> None:
    """Catch incorrect date arithmetic, weekday wrapping and normalization."""
    from members.mikaelvo639.w3.dates import parse_due

    assert parse_due(text, date(2026, 10, 26)) == expected


@pytest.mark.parametrize("text", ["", "yesterday", "in -1 days", "2026-02-30", "20261030"])
def test_parse_due_rejects_unknown_or_invalid_dates(text: str) -> None:
    """Catch permissive acceptance of unsupported text or impossible dates."""
    from members.mikaelvo639.w3.dates import parse_due

    with pytest.raises(ValueError):
        parse_due(text, date(2026, 10, 26))


def test_parse_due_crosses_year_boundary() -> None:
    """Catch day arithmetic implemented by replacing the day number."""
    from members.mikaelvo639.w3.dates import parse_due

    assert parse_due("tomorrow", date(2026, 12, 31)) == date(2027, 1, 1)
