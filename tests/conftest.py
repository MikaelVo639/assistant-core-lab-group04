"""Load a fresh copy of the original script for each characterisation test."""

import importlib.util
from pathlib import Path
from types import ModuleType

import pytest


@pytest.fixture
def monolith() -> ModuleType:
    path = Path(__file__).resolve().parents[1] / "lab03" / "monolith" / "assistant_monolith.py"
    spec = importlib.util.spec_from_file_location("lab03_original", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.load()
    return module
