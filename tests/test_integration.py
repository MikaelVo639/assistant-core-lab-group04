"""Verify the complete package with real data, routing, models, tools, and logs."""

import json
import subprocess
import sys
from pathlib import Path

import pytest

from assistant_core.config import Settings
from assistant_core.knowledge import Handbook, OfficeDirectory
from assistant_core.logging_setup import setup_logging
from assistant_core.models import Intent, Message
from assistant_core.responder import StubLLMResponder
from assistant_core.service import AssistantService


@pytest.fixture
def real_service():
    data = Path(__file__).resolve().parents[1] / "data"
    return AssistantService(
        Settings(data_dir=data),
        OfficeDirectory.from_csv(data / "offices.csv"),
        Handbook.from_json(data / "handbook.json"),
        StubLLMResponder(),
    )


@pytest.mark.parametrize(
    "question,intent,fragment",
    [
        ("hello", Intent.GREETING, "offices, fees and rules"),
        ("tuition for 18 credits and 2 retake", Intent.FEE, "9,450,000"),
        ("where is the library", Intent.OFFICE, "B.201"),
        ("thesis registration credits", Intent.RULE, "120 accumulated credits"),
        ("weather tomorrow", Intent.UNKNOWN, "don't know"),
    ],
)
def test_complete_service_flows(real_service, question, intent, fragment):
    response = real_service.handle(Message(text=question))
    assert response.intent is intent and fragment in response.answer
    if intent is Intent.RULE:
        assert response.sources[0].id == "H26-5.3"


def test_real_provider_fallback_preserves_source_and_writes_safe_json(real_service, capsys):
    setup_logging("INFO")
    real_service.responder = StubLLMResponder(fail=True)
    response = real_service.handle(Message(text="thesis registration credits"))
    assert response.degraded and response.sources[0].id == "H26-5.3"
    output = capsys.readouterr()
    records = [json.loads(line) for line in output.err.splitlines()]
    assert output.out == "" and records[-1]["degraded"] is True
    assert "thesis registration credits" not in output.err


def test_cli_runs_from_another_directory_with_configured_data(tmp_path, cli_environment):
    result = subprocess.run(
        [sys.executable, "-B", "-m", "assistant_core", "tuition for 18 credits and 2 retake"],
        cwd=tmp_path,
        env=cli_environment,
        text=True,
        capture_output=True,
        check=False,
        timeout=10,
    )
    assert result.returncode == 0 and result.stdout == "Your tuition is 9,450,000 VND.\n"
    record = json.loads(result.stderr)
    assert record["intent"] == "fee" and record["degraded"] is False


def test_missing_handbook_fails_before_answering(tmp_path, cli_environment):
    root = Path(__file__).resolve().parents[1]
    (tmp_path / "offices.csv").write_bytes((root / "data/offices.csv").read_bytes())
    env = dict(cli_environment, ASSISTANT_DATA_DIR=str(tmp_path))
    result = subprocess.run(
        [sys.executable, "-B", "-m", "assistant_core", "hello"],
        cwd=tmp_path,
        env=env,
        text=True,
        capture_output=True,
        check=False,
        timeout=10,
    )
    assert result.returncode == 2 and result.stdout == ""
    assert "Cannot start" in result.stderr and "Traceback" not in result.stderr


def test_cli_selects_template_provider_and_displays_source(cli_environment):
    result = subprocess.run(
        [sys.executable, "-B", "-m", "assistant_core", "thesis?"],
        env=dict(cli_environment, LLM_PROVIDER="template"),
        text=True,
        capture_output=True,
        check=False,
        timeout=10,
    )
    assert result.returncode == 0
    assert result.stdout.startswith("Thesis registration: Students may register")
    assert "(source: H26-5.3)" in result.stdout
    record = json.loads(result.stderr)
    assert record["intent"] == "rule" and record["degraded"] is False
