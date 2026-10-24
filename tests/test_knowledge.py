"""Unit tests for the knowledge module (OfficeDirectory and Handbook).

Tests verify data ingestion, factory methods (from_csv, from_json),
query lookups (find, names, search), error handling (missing files, malformed data),
and fallback response formatting.
"""

from pathlib import Path

import pytest

from assistant_core.errors import DataError
from assistant_core.knowledge import Handbook, Office, OfficeDirectory, Rule

DATA_DIR = Path(__file__).resolve().parent.parent / "data"


# ==============================================================================
# OfficeDirectory Tests
# ==============================================================================


def test_office_directory_loads_real_data() -> None:
    """Ensure real offices.csv loads correctly and contains expected departments."""
    directory = OfficeDirectory.from_csv(DATA_DIR / "offices.csv")
    assert len(directory.offices) >= 4
    assert "library" in directory.names

    office = directory.find("where is the library")
    assert office is not None
    assert office.name == "Library"
    assert office.room == "B.201"
    assert office.hours == "Mon-Sat 07:00-20:00"


def test_office_directory_lookup_formatted() -> None:
    """Ensure lookup_formatted returns expected string format identical to monolith."""
    directory = OfficeDirectory(DATA_DIR)
    formatted = directory.lookup_formatted("where is the library")
    assert formatted == "Library: room B.201, open Mon-Sat 07:00-20:00"


def test_office_directory_dict_constructor() -> None:
    """Ensure constructor accepting direct dictionary works."""
    dummy = Office(name="Dean", room="A.100", hours="Mon-Fri 09:00-11:00")
    directory = OfficeDirectory({"dean": dummy})
    assert directory.names == {"dean"}
    assert directory.find("see the dean") == dummy


def test_office_directory_case_insensitive() -> None:
    """Lookup should match regardless of casing."""
    directory = OfficeDirectory(DATA_DIR)
    assert directory.find("STUDENT AFFAIRS") is not None
    assert directory.lookup("training office") is not None


def test_office_directory_not_found() -> None:
    """Unknown offices should return None cleanly without error."""
    directory = OfficeDirectory(DATA_DIR)
    assert directory.find("swimming pool") is None
    assert directory.lookup_formatted("weather tomorrow") is None


def test_office_directory_missing_file(tmp_path: Path) -> None:
    """Non-existent CSV file must raise DataError."""
    with pytest.raises(DataError, match="Office file not found"):
        OfficeDirectory.from_csv(tmp_path / "non_existent.csv")


def test_office_directory_empty_file(tmp_path: Path) -> None:
    """Empty CSV file must raise DataError."""
    empty_csv = tmp_path / "offices.csv"
    empty_csv.write_text("", encoding="utf-8")

    with pytest.raises(DataError, match="empty"):
        OfficeDirectory.from_csv(empty_csv)


def test_office_directory_invalid_header(tmp_path: Path) -> None:
    """CSV with invalid headers must raise DataError."""
    bad_csv = tmp_path / "offices.csv"
    bad_csv.write_text("department,location,schedule\nIT,E.005,08:00\n", encoding="utf-8")

    with pytest.raises(DataError, match="Invalid CSV headers"):
        OfficeDirectory.from_csv(bad_csv)


def test_office_directory_malformed_row(tmp_path: Path) -> None:
    """CSV with missing columns in a row must raise DataError."""
    bad_csv = tmp_path / "offices.csv"
    bad_csv.write_text("name,room,hours\nLibrary,B.201\n", encoding="utf-8")

    with pytest.raises(DataError, match="Malformed row"):
        OfficeDirectory.from_csv(bad_csv)


# ==============================================================================
# Handbook Tests
# ==============================================================================


def test_handbook_loads_real_data() -> None:
    """Ensure real handbook.json loads correctly and search finds relevant regulations."""
    handbook = Handbook.from_json(DATA_DIR / "handbook.json")
    assert len(handbook.rules) >= 5

    rule = handbook.search("can I register my thesis with 118 credits")
    assert rule is not None
    assert rule.id == "H26-5.3"
    assert rule.title == "Thesis registration"
    assert rule.source.id == "H26-5.3"
    assert rule.source.title == "Thesis registration"
    assert "Students may register a thesis" in rule.text


def test_handbook_search_match_wrapper() -> None:
    """Ensure search_match returns RuleMatch with score."""
    handbook = Handbook(DATA_DIR)
    match = handbook.search_match("can I register my thesis with 118 credits")
    assert match is not None
    assert match.score >= 1
    assert match.id == "H26-5.3"


def test_handbook_list_constructor() -> None:
    """Ensure constructor accepting list of rules works."""
    dummy_rule = Rule(id="T1", title="Test Rule", text="Students must follow the test rule.")
    handbook = Handbook([dummy_rule])
    assert len(handbook.rules) == 1
    assert handbook.search("must follow the test rule") == dummy_rule


def test_handbook_search_formatted_fallback() -> None:
    """Ensure search_formatted_fallback outputs source citation matching monolith."""
    handbook = Handbook(DATA_DIR)
    answer = handbook.search_formatted_fallback("can I register my thesis with 118 credits")
    expected = (
        "Students may register a thesis when they have at least 120 accumulated credits "
        "and a GPA of at least 2.0. (source: H26-5.3)"
    )
    assert answer == expected


def test_handbook_search_not_found() -> None:
    """Irrelevant query should return None."""
    handbook = Handbook(DATA_DIR)
    assert handbook.search("what is the weather today") is None
    assert handbook.search_formatted_fallback("what is the weather today") is None


def test_handbook_search_only_short_words() -> None:
    """Queries with only words <= 3 chars should return None without error."""
    handbook = Handbook(DATA_DIR)
    assert handbook.search("is it on") is None


def test_handbook_missing_file(tmp_path: Path) -> None:
    """Non-existent handbook JSON file must raise DataError."""
    with pytest.raises(DataError, match="Handbook file not found"):
        Handbook.from_json(tmp_path / "non_existent.json")


def test_handbook_invalid_json_syntax(tmp_path: Path) -> None:
    """Corrupted JSON syntax must raise DataError."""
    bad_json = tmp_path / "handbook.json"
    bad_json.write_text("{bad json syntax", encoding="utf-8")

    with pytest.raises(DataError, match="Invalid JSON format"):
        Handbook.from_json(bad_json)


def test_handbook_not_a_list(tmp_path: Path) -> None:
    """Handbook JSON top-level that is not a list must raise DataError."""
    bad_json = tmp_path / "handbook.json"
    bad_json.write_text('{"rules": []}', encoding="utf-8")

    with pytest.raises(DataError, match="must be a list"):
        Handbook.from_json(bad_json)


def test_handbook_empty_list(tmp_path: Path) -> None:
    """Empty rule list must raise DataError."""
    bad_json = tmp_path / "handbook.json"
    bad_json.write_text("[]", encoding="utf-8")

    with pytest.raises(DataError, match="empty"):
        Handbook.from_json(bad_json)


def test_handbook_missing_required_field(tmp_path: Path) -> None:
    """Rule item missing required keys must raise DataError."""
    bad_json = tmp_path / "handbook.json"
    bad_json.write_text('[{"id": "H1", "title": "Test"}]', encoding="utf-8")

    with pytest.raises(DataError, match="Missing or invalid field 'text'"):
        Handbook.from_json(bad_json)
