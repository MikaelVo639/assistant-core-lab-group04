"""Load a fresh copy of the original script for each characterisation test."""

import importlib.util
import sys
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


@pytest.fixture
def core_contracts(monkeypatch: pytest.MonkeyPatch):
    """Supply only missing collaborators; do not mock the service or CLI under test."""
    from component_contracts import install_contracts

    package = importlib.import_module("assistant_core")
    missing = object()
    names = ("service", "__main__")
    old_attributes = {name: package.__dict__.get(name, missing) for name in names}
    old_modules = {name: sys.modules.get(f"assistant_core.{name}", missing) for name in names}
    for name in names:
        package.__dict__.pop(name, None)
        sys.modules.pop(f"assistant_core.{name}", None)
    try:
        yield install_contracts(monkeypatch)
    finally:
        # Restore both import paths, including package attributes that bypass sys.modules.
        for name in names:
            if old_attributes[name] is missing:
                package.__dict__.pop(name, None)
            else:
                setattr(package, name, old_attributes[name])
            if old_modules[name] is missing:
                sys.modules.pop(f"assistant_core.{name}", None)
            else:
                sys.modules[f"assistant_core.{name}"] = old_modules[name]
