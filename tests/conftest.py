"""Load a fresh copy of the original script for each characterisation test."""

import importlib.util
import logging
import os
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
def core_contracts():
    """Supply real collaborators and restore the component imports after each test."""
    from component_fixtures import collaborator_scope

    with collaborator_scope() as collaborators:
        yield collaborators


@pytest.fixture(autouse=True)
def preserve_application_logging():
    """Do not retain handlers bound to pytest capture streams between tests."""
    logger = logging.getLogger("assistant_core")
    handlers, level, propagate = logger.handlers[:], logger.level, logger.propagate
    yield
    for handler in logger.handlers[:]:
        if handler not in handlers:
            logger.removeHandler(handler)
            handler.close()
    logger.handlers = handlers
    logger.setLevel(level)
    logger.propagate = propagate


@pytest.fixture
def cli_environment():
    """Make process-level assertions independent of shell configuration and local dotenv files."""
    root = Path(__file__).resolve().parents[1]
    return dict(
        os.environ,
        PYTHONPATH=str(root / "src"),
        ASSISTANT_DATA_DIR=str(root / "data"),
        LLM_PROVIDER="stub",
        LLM_API_KEY="",
        CREDIT_RATE_VND="450000",
        RETAKE_MULTIPLIER="1.5",
        MAX_CREDITS="30",
        LOG_LEVEL="INFO",
    )
