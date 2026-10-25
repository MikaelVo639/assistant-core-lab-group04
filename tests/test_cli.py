"""Test the CLI boundary and composition separately from missing collaborators."""

import importlib
import logging
import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest


@pytest.fixture
def cli(core_contracts):
    return importlib.import_module("assistant_core.__main__")


def run_cli(*args):
    env = dict(os.environ, PYTHONPATH=str(Path(__file__).resolve().parents[1] / "src"))
    return subprocess.run(
        [sys.executable, "-B", "-m", "assistant_core", *args],
        text=True,
        capture_output=True,
        env=env,
        check=False,
        timeout=10,
    )


def test_help_works_without_the_other_members_modules():
    result = run_cli("--help")
    assert result.returncode == 0
    assert "usage:" in result.stdout and "text" in result.stdout
    assert result.stderr == ""


def test_rejected_command_line_arguments_do_not_echo_sensitive_values():
    result = run_cli("--private-api-key=secret-example", "hello")
    assert result.returncode == 2 and result.stdout == ""
    assert "secret-example" not in result.stderr
    assert "--private-api-key" not in result.stderr
    assert "--help" in result.stderr


def test_cli_joins_words_and_preserves_session(cli, core_contracts, monkeypatch, capsys, caplog):
    c = core_contracts
    service_module = importlib.import_module("assistant_core.service")
    service = service_module.AssistantService(c.settings, c.offices, c.handbook, c.responder.StubLLMResponder())

    def route(text, names):
        assert text == "hello team"
        return c.models.Intent.GREETING

    monkeypatch.setattr(service_module, "route", route)
    monkeypatch.setattr(cli, "build_service", lambda: service)
    with caplog.at_level(logging.INFO, logger="assistant_core"):
        status = cli.main(["--session-id", "student-1", "hello", "team"])
    output = capsys.readouterr()
    assert status == 0
    assert output.out == "Hello! I can help with offices, fees and rules.\n"
    assert output.err == ""
    assert [record.session for record in caplog.records if record.getMessage() == "handled"] == ["student-1"]


@pytest.mark.parametrize("text", ["", "x" * 2001], ids=["empty", "too-long"])
def test_invalid_message_is_rejected_before_startup(cli, monkeypatch, capsys, text):
    def unexpected_startup():
        pytest.fail("Invalid input must be rejected before loading data")

    monkeypatch.setattr(cli, "build_service", unexpected_startup)
    assert cli.main([text]) == 2
    output = capsys.readouterr()
    assert output.out == "" and "Invalid" in output.err
    assert "Traceback" not in output.err and "x" * 100 not in output.err


@pytest.mark.parametrize("error_type", ["ConfigError", "DataError"])
def test_startup_errors_are_safe_and_go_to_stderr(cli, core_contracts, monkeypatch, capsys, error_type):
    def fail():
        raise getattr(core_contracts.errors, error_type)("private-api-key or provider details")

    monkeypatch.setattr(cli, "build_service", fail)
    assert cli.main(["hello"]) == 2
    output = capsys.readouterr()
    assert output.out == "" and "Cannot start" in output.err
    assert "private-api-key" not in output.err and "Traceback" not in output.err


def test_configuration_validation_does_not_expose_values(cli, core_contracts, monkeypatch, capsys):
    def fail():
        # Use a real Pydantic validation error with an input that must not be printed.
        core_contracts.models.Message(text="private-value-" * 200)

    monkeypatch.setattr(cli, "build_service", fail)
    assert cli.main(["hello"]) == 2
    output = capsys.readouterr()
    assert output.out == "" and "Invalid" in output.err
    assert "private-value" not in output.err


def test_build_service_uses_the_configured_data_directory(cli, core_contracts, monkeypatch, tmp_path):
    c = core_contracts
    c.settings = c.settings.model_copy(update={"data_dir": tmp_path})
    monkeypatch.setattr(c.config, "load_settings", lambda: c.settings)

    def load_offices(path):
        assert path == tmp_path / "offices.csv"
        return c.offices

    def load_handbook(path):
        assert path == tmp_path / "handbook.json"
        return c.handbook

    monkeypatch.setattr(c.knowledge, "OfficeDirectory", SimpleNamespace(from_csv=load_offices))
    monkeypatch.setattr(c.knowledge, "Handbook", SimpleNamespace(from_json=load_handbook))
    levels = []
    monkeypatch.setattr(c.logging_setup, "setup_logging", levels.append)
    service = cli.build_service()
    result = service.handle(c.models.Message(text="thesis registration credits"))
    assert result.intent is c.models.Intent.RULE and result.sources[0].id == "H26-5.3"
    assert levels == ["INFO"]


def test_build_service_rejects_a_provider_that_lab03_does_not_implement(cli, core_contracts, monkeypatch):
    c = core_contracts
    c.settings = c.settings.model_copy(update={"llm_provider": "unimplemented-provider"})
    monkeypatch.setattr(c.config, "load_settings", lambda: c.settings)
    with pytest.raises(c.errors.ConfigError):
        cli.build_service()


def test_missing_package_components_have_a_clear_startup_error(cli, monkeypatch, capsys):
    def fail():
        raise ModuleNotFoundError("missing component", name="assistant_core.knowledge")

    monkeypatch.setattr(cli, "build_service", fail)
    assert cli.main(["hello"]) == 2
    output = capsys.readouterr()
    assert output.out == "" and "Cannot start" in output.err
    assert "modules" in output.err and "Traceback" not in output.err


def test_unrelated_import_defects_are_not_reported_as_pending_team_modules(cli, monkeypatch):
    def fail():
        raise ModuleNotFoundError("a programming error", name="unrelated_internal_typo")

    monkeypatch.setattr(cli, "build_service", fail)
    with pytest.raises(ModuleNotFoundError, match="programming error"):
        cli.main(["hello"])
