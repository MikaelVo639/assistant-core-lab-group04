"""Knowledge management module for assistant_core.

This module provides data loading, validation, and search capabilities for
office directories and student handbook regulations. Developed by Đăng.
"""

from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path

from assistant_core.errors import DataError
from assistant_core.models import Source


def _query_words(query: str) -> list[str]:
    """Normalize keyword tokens consistently for lookup and relevance scores."""
    return [word for word in re.findall(r"\w+", query.casefold()) if len(word) > 3]


@dataclass(frozen=True)
class Office:
    """Represents a university office or department."""

    name: str
    room: str
    hours: str

    def format_response(self) -> str:
        """Format the office details into a user-facing string."""
        return f"{self.name}: room {self.room}, open {self.hours}"


class OfficeDirectory:
    """Manages office records and handles office location/hours lookup."""

    def __init__(
        self,
        target: dict[str, Office] | Path | str | None = None,
        *,
        offices: dict[str, Office] | None = None,
    ) -> None:
        """Initialize with an office dictionary or a path to CSV/data directory.

        Args:
            target: Either a dictionary mapping lowercase names to Office objects,
                    a Path/string to offices.csv, or a directory containing offices.csv.
        """
        if offices is not None:
            if target is not None:
                raise TypeError("Pass only one office input.")
            target = offices
        if target is None:
            raise TypeError("OfficeDirectory requires office data or a path.")
        if isinstance(target, dict):
            self._offices = dict(target)
            self._file_path: Path | None = None
        else:
            raw_path = Path(target)
            self._file_path = raw_path / "offices.csv" if raw_path.is_dir() else raw_path
            self._offices = {}
            self._load_from_path(self._file_path)

    @classmethod
    def from_csv(cls, path: Path | str) -> OfficeDirectory:
        """Construct an OfficeDirectory from a CSV file or directory."""
        return cls(path)

    @property
    def file_path(self) -> Path | None:
        """Return the resolved CSV path, if loaded from file."""
        return self._file_path

    @property
    def names(self) -> set[str]:
        """Return lowercase office names for router matching."""
        return set(self._offices)

    @property
    def offices(self) -> list[Office]:
        """Return all loaded office instances."""
        return list(self._offices.values())

    def _load_from_path(self, path: Path) -> None:
        """Load and validate records from the specified CSV file."""
        if not path.exists():
            raise DataError(f"Office file not found: {path}")

        try:
            with path.open(encoding="utf-8", newline="") as f:
                reader = csv.reader(f)
                try:
                    header = next(reader)
                except StopIteration:
                    raise DataError(f"Office file is empty: {path}") from None

                clean_header = [col.strip().lower() for col in header]
                required_cols = ["name", "room", "hours"]
                if not set(required_cols).issubset(clean_header):
                    raise DataError(f"Invalid CSV headers in {path}: expected {required_cols}, got {clean_header}")
                column_indices = [clean_header.index(column) for column in required_cols]

                for line_idx, row in enumerate(reader, start=2):
                    if not row or not any(field.strip() for field in row):
                        continue
                    if any(i >= len(row) or not row[i].strip() for i in column_indices):
                        raise DataError(f"Malformed row at line {line_idx} in {path}: {row}")

                    name, room, hours = (row[i].strip() for i in column_indices)
                    if name.lower() in self._offices:
                        raise DataError(f"Duplicate office name at line {line_idx} in {path}")
                    self._offices[name.lower()] = Office(name=name, room=room, hours=hours)

        except (OSError, UnicodeError, csv.Error) as exc:
            raise DataError(f"Failed to read office file {path}: {exc}") from exc

        if not self._offices:
            raise DataError(f"No valid office records found in {path}")

    def find(self, text: str) -> Office | None:
        """Find an office matching any keyword in the query text."""
        t = text.lower()
        return next((o for name, o in self._offices.items() if name in t), None)

    def lookup(self, query: str) -> Office | None:
        """Alias for find() for convenience."""
        return self.find(query)

    def lookup_formatted(self, query: str) -> str | None:
        """Find an office and return its formatted response string."""
        office = self.find(query)
        return office.format_response() if office else None


@dataclass(frozen=True)
class Rule:
    """Represents a student handbook regulation."""

    id: str
    title: str
    text: str

    @property
    def source(self) -> Source:
        """Return citation source for this rule."""
        return Source(id=self.id, title=self.title)

    def format_fallback_response(self) -> str:
        """Format rule text and source for fallback when LLM fails."""
        return f"{self.text} (source: {self.id})"


# Backward compatibility alias
HandbookRule = Rule


@dataclass(frozen=True)
class RuleMatch:
    """Represents a matched rule and its matching score."""

    rule: Rule
    score: int

    @property
    def id(self) -> str:
        return self.rule.id

    @property
    def title(self) -> str:
        return self.rule.title

    @property
    def text(self) -> str:
        return self.rule.text

    @property
    def source(self) -> Source:
        return self.rule.source

    def format_fallback_response(self) -> str:
        return self.rule.format_fallback_response()


class Handbook:
    """Manages student handbook rules and handles rule searching."""

    def __init__(
        self,
        target: list[Rule] | Path | str | None = None,
        *,
        rules: list[Rule] | None = None,
    ) -> None:
        """Initialize with a list of rules or a path to JSON/data directory."""
        if rules is not None:
            if target is not None:
                raise TypeError("Pass only one handbook input.")
            target = rules
        if target is None:
            raise TypeError("Handbook requires rules or a path.")
        if isinstance(target, list):
            self._rules = list(target)
            self._file_path: Path | None = None
        else:
            raw_path = Path(target)
            self._file_path = raw_path / "handbook.json" if raw_path.is_dir() else raw_path
            self._rules = []
            self._load_from_path(self._file_path)

    @classmethod
    def from_json(cls, path: Path | str) -> Handbook:
        """Construct a Handbook from a JSON file or directory."""
        return cls(path)

    @property
    def file_path(self) -> Path | None:
        """Return the resolved JSON path, if loaded from file."""
        return self._file_path

    @property
    def rules(self) -> list[Rule]:
        """Return all loaded handbook rules."""
        return list(self._rules)

    def _load_from_path(self, path: Path) -> None:
        """Load and validate rules from the JSON file."""
        if not path.exists():
            raise DataError(f"Handbook file not found: {path}")

        try:
            with path.open(encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as exc:
            raise DataError(f"Invalid JSON format in {path}: {exc}") from exc
        except (OSError, UnicodeError) as exc:
            raise DataError(f"Failed to read handbook file {path}: {exc}") from exc

        if not isinstance(data, list):
            raise DataError(f"Handbook JSON must be a list of rules in {path}")

        if not data:
            raise DataError(f"Handbook file is empty in {path}")

        identifiers: set[str] = set()
        for idx, item in enumerate(data):
            if not isinstance(item, dict):
                raise DataError(f"Invalid rule item at index {idx} in {path}: must be an object")

            for required_field in ("id", "title", "text"):
                val = item.get(required_field)
                if not isinstance(val, str) or not val.strip():
                    raise DataError(f"Missing or invalid field '{required_field}' at rule index {idx} in {path}")

            identifier = item["id"].strip()
            if identifier in identifiers:
                raise DataError(f"Duplicate rule ID at index {idx} in {path}")
            identifiers.add(identifier)
            self._rules.append(
                Rule(
                    id=identifier,
                    title=item["title"].strip(),
                    text=item["text"].strip(),
                )
            )

    def search(self, query: str) -> Rule | None:
        """Search for the most relevant rule matching query tokens > 3 chars.

        Returns:
            The highest-scoring Rule if score >= 1, else None.
        """
        query_words = _query_words(query)
        if not query_words:
            return None

        best_rule: Rule | None = None
        best_score = 0

        for rule in self._rules:
            rule_text_lower = rule.text.casefold()
            score = sum(1 for w in query_words if w in rule_text_lower)
            if score > best_score:
                best_score = score
                best_rule = rule

        if best_rule is not None and best_score >= 1:
            return best_rule
        return None

    def search_match(self, query: str) -> RuleMatch | None:
        """Search and return RuleMatch with relevance score."""
        rule = self.search(query)
        if rule is None:
            return None
        words = _query_words(query)
        score = sum(1 for w in words if w in rule.text.casefold())
        return RuleMatch(rule=rule, score=score)

    def search_formatted_fallback(self, query: str) -> str | None:
        """Search and format the response using the deterministic fallback template."""
        rule = self.search(query)
        return rule.format_fallback_response() if rule else None
