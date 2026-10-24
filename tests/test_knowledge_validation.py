"""Check knowledge loading, deterministic search and named startup failures."""

import importlib
import json
from pathlib import Path

import pytest

from assistant_core.errors import DataError


@pytest.fixture
def knowledge():
    return importlib.import_module("assistant_core.knowledge")


def test_real_course_data_lookup_and_search(knowledge):
    data = Path(__file__).resolve().parents[1] / "data"
    directory = knowledge.OfficeDirectory.from_csv(data / "offices.csv")
    office = directory.find("WHERE IS THE LIBRARY?")
    assert office.name == "Library" and office.room == "B.201"
    assert "library" in directory.names
    assert directory.find("unknown building") is None
    handbook = knowledge.Handbook.from_json(data / "handbook.json")
    assert handbook.search("thesis registration credits").id == "H26-5.3"
    assert handbook.search("weather tomorrow") is None


@pytest.mark.parametrize("loader,suffix", [("from_csv", "offices.csv"), ("from_json", "handbook.json")])
def test_missing_file_is_a_named_data_error(knowledge, tmp_path, loader, suffix):
    cls = knowledge.OfficeDirectory if loader == "from_csv" else knowledge.Handbook
    with pytest.raises(DataError):
        getattr(cls, loader)(tmp_path / suffix)


@pytest.mark.parametrize("content", ["", "bad,headers\na,b\n", "name,room,hours\nLibrary,,Monday\n"])
def test_invalid_office_files_are_rejected(knowledge, tmp_path, content):
    path = tmp_path / "offices.csv"
    path.write_text(content, encoding="utf-8")
    with pytest.raises(DataError):
        knowledge.OfficeDirectory.from_csv(path)


@pytest.mark.parametrize("content", ["not-json", "{}", "[]", '[{"id":"x","title":"Missing text"}]'])
def test_invalid_handbook_files_are_rejected(knowledge, tmp_path, content):
    path = tmp_path / "handbook.json"
    path.write_text(content, encoding="utf-8")
    with pytest.raises(DataError):
        knowledge.Handbook.from_json(path)


def test_duplicate_rule_ids_are_rejected(knowledge, tmp_path):
    path = tmp_path / "handbook.json"
    rule = {"id": "same", "title": "Title", "text": "Rule text"}
    path.write_text(json.dumps([rule, rule]), encoding="utf-8")
    with pytest.raises(DataError):
        knowledge.Handbook.from_json(path)


@pytest.mark.parametrize(
    "filename,content",
    [
        ("offices.csv", b"name,room,hours\nLibrary,\xff,Monday\n"),
        ("handbook.json", b"\xff"),
    ],
)
def test_unreadable_encoding_is_a_named_data_error(knowledge, tmp_path, filename, content):
    path = tmp_path / filename
    path.write_bytes(content)
    loader = knowledge.OfficeDirectory.from_csv if filename.endswith("csv") else knowledge.Handbook.from_json
    with pytest.raises(DataError):
        loader(path)


def test_duplicate_office_names_are_rejected_case_insensitively(knowledge, tmp_path):
    path = tmp_path / "offices.csv"
    path.write_text("name,room,hours\nLibrary,A.1,Monday\nLIBRARY,A.2,Tuesday\n", encoding="utf-8")
    with pytest.raises(DataError):
        knowledge.OfficeDirectory.from_csv(path)


@pytest.mark.parametrize("query", ["thesis?", "THESIS? registration!"])
def test_punctuation_search_and_match_score_use_the_same_keywords(knowledge, query):
    handbook = knowledge.Handbook([knowledge.Rule("r1", "Thesis", "Thesis registration requires credits.")])
    rule = handbook.search(query)
    match = handbook.search_match(query)
    assert rule is not None and match is not None
    assert match.id == rule.id == "r1" and match.score >= 1


@pytest.mark.parametrize(
    "class_name,keyword,value",
    [
        ("OfficeDirectory", "offices", {}),
        ("Handbook", "rules", []),
        ("OfficeDirectory", "target", {}),
        ("Handbook", "target", []),
    ],
)
def test_existing_and_merged_constructor_keywords_are_compatible(knowledge, class_name, keyword, value):
    obj = getattr(knowledge, class_name)(**{keyword: value})
    if class_name == "OfficeDirectory":
        assert obj.names == set()
    else:
        assert obj.search("thesis") is None


@pytest.mark.parametrize(
    "content",
    [
        "hours,name,room\nMonday,Library,A.1\n",
        "note,hours,name,room\nOptional,Monday,Library,A.1\n",
    ],
)
def test_office_csv_reads_required_columns_by_name(knowledge, tmp_path, content):
    path = tmp_path / "offices.csv"
    path.write_text(content, encoding="utf-8")
    office = knowledge.OfficeDirectory.from_csv(path).find("library")
    assert office is not None and (office.name, office.room, office.hours) == ("Library", "A.1", "Monday")
