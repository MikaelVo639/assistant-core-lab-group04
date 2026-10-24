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
