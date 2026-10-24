"""Load immutable knowledge records and search them through focused objects."""

import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path

from assistant_core.errors import DataError


@dataclass(frozen=True)
class Office:
    """A named office with its room and opening hours."""

    name: str
    room: str
    hours: str


@dataclass(frozen=True)
class Rule:
    """A handbook rule with stable source identity."""

    id: str
    title: str
    text: str


class OfficeDirectory:
    """Own office records instead of sharing mutable module-level data."""

    def __init__(self, offices: dict[str, Office]):
        self._offices = dict(offices)

    @classmethod
    def from_csv(cls, path: Path) -> "OfficeDirectory":
        """Validate office CSV structure and fail clearly at startup."""
        try:
            with path.open(encoding="utf-8", newline="") as stream:
                reader = csv.DictReader(stream)
                if not {"name", "room", "hours"}.issubset(reader.fieldnames or []):
                    raise DataError("Office data requires name, room, and hours columns.")
                offices = {}
                for row in reader:
                    if not all(isinstance(row.get(key), str) and row[key].strip() for key in ("name", "room", "hours")):
                        raise DataError("Office data contains an incomplete record.")
                    office = Office(*(row[key].strip() for key in ("name", "room", "hours")))
                    key = office.name.casefold()
                    if key in offices:
                        raise DataError("Office data contains a duplicate name.")
                    offices[key] = office
        except (OSError, UnicodeError, csv.Error):
            raise DataError("Cannot read office data.") from None
        if not offices:
            raise DataError("Office data is empty.")
        return cls(offices)

    @property
    def names(self) -> set[str]:
        """Return a defensive copy of office names for the router."""
        return set(self._offices)

    def find(self, text: str) -> Office | None:
        """Find the first office mentioned in a case-insensitive query."""
        query = text.casefold()
        return next((office for name, office in self._offices.items() if name in query), None)


class Handbook:
    """Own handbook records and provide deterministic baseline keyword search."""

    def __init__(self, rules: list[Rule]):
        self._rules = tuple(rules)

    @classmethod
    def from_json(cls, path: Path) -> "Handbook":
        """Load non-empty, uniquely identified rules or raise a named data error."""
        try:
            with path.open(encoding="utf-8") as stream:
                records = json.load(stream)
        except (OSError, UnicodeError, json.JSONDecodeError):
            raise DataError("Cannot read handbook data.") from None
        if not isinstance(records, list) or not records:
            raise DataError("Handbook data must be a non-empty list.")
        rules = []
        identifiers = set()
        for record in records:
            if not isinstance(record, dict) or not all(
                isinstance(record.get(key), str) and record[key].strip() for key in ("id", "title", "text")
            ):
                raise DataError("Handbook data contains an incomplete record.")
            rule = Rule(*(record[key].strip() for key in ("id", "title", "text")))
            if rule.id in identifiers:
                raise DataError("Handbook data contains a duplicate rule ID.")
            identifiers.add(rule.id)
            rules.append(rule)
        return cls(rules)

    def search(self, query: str) -> Rule | None:
        """Choose the highest keyword-overlap rule, preserving file order for ties."""
        words = [word for word in re.findall(r"\w+", query.casefold()) if len(word) > 3]
        best = None
        best_score = 0
        for rule in self._rules:
            score = sum(word in rule.text.casefold() for word in words)
            if score > best_score:
                best, best_score = rule, score
        return best
