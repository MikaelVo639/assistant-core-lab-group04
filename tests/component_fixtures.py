"""Build real collaborators with small deterministic records for component tests."""

import importlib
import sys
from contextlib import contextmanager
from types import SimpleNamespace


@contextmanager
def collaborator_scope():
    """Isolate module imports without depending on pytest's conftest module name."""
    package = importlib.import_module("assistant_core")
    missing = object()
    names = ("service", "__main__")
    old_attributes = {name: package.__dict__.get(name, missing) for name in names}
    old_modules = {name: sys.modules.get(f"assistant_core.{name}", missing) for name in names}
    for name in names:
        package.__dict__.pop(name, None)
        sys.modules.pop(f"assistant_core.{name}", None)
    try:
        yield make_collaborators()
    finally:
        for name in names:
            if old_attributes[name] is missing:
                package.__dict__.pop(name, None)
            else:
                setattr(package, name, old_attributes[name])
            if old_modules[name] is missing:
                sys.modules.pop(f"assistant_core.{name}", None)
            else:
                sys.modules[f"assistant_core.{name}"] = old_modules[name]


def make_collaborators() -> SimpleNamespace:
    """Create actual domain objects; no missing production modules are substituted."""
    modules = {
        name: importlib.import_module(f"assistant_core.{name}")
        for name in ("errors", "models", "responder", "router", "tools", "config", "knowledge", "logging_setup")
    }
    knowledge = modules["knowledge"]
    office = knowledge.Office("Library", "B.201", "Mon-Sat 07:00-20:00")
    rule = knowledge.Rule(
        "H26-5.3",
        "Thesis registration",
        "Students may register a thesis when they have at least 120 accumulated credits and a GPA of at least 2.0.",
    )
    return SimpleNamespace(
        **modules,
        settings=modules["config"].Settings(),
        office=office,
        rule=rule,
        offices=knowledge.OfficeDirectory({"library": office}),
        handbook=knowledge.Handbook([rule]),
    )
