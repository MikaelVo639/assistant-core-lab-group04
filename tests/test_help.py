"""H1: capability discovery stays deterministic and reflects the configured service."""

import json
import subprocess
import sys

import pytest

from assistant_core.config import Settings
from assistant_core.knowledge import Handbook, Office, OfficeDirectory
from assistant_core.models import Message
from assistant_core.responder import StubLLMResponder
from assistant_core.router import route
from assistant_core.service import AssistantService


@pytest.mark.parametrize("question", ["help", "HELP!", "what can you do?", "hello, help", "  hi   help  "])
def test_help_aliases_have_a_typed_help_intent(question):
    assert route(question, {"it helpdesk"}).value == "help"


@pytest.mark.parametrize(
    "question,expected",
    [
        ("where is IT Helpdesk", "office"),
        ("help with tuition for 12 credits", "fee"),
        ("help with thesis registration", "rule"),
    ],
)
def test_help_does_not_steal_existing_domain_questions(question, expected):
    assert route(question, {"it helpdesk"}).value == expected


def test_help_examples_reflect_settings_and_available_offices_without_provider_calls(monkeypatch):
    settings = Settings(max_credits=5, credit_rate_vnd=500_000)
    offices = OfficeDirectory({"registrar": Office("Registrar", "A.1", "Monday")})
    handbook = Handbook([])

    def unexpected_search(query):
        pytest.fail("Help must not query the handbook or a provider")

    monkeypatch.setattr(handbook, "search", unexpected_search)
    service = AssistantService(settings, offices, handbook, StubLLMResponder(fail=True))
    response = service.handle(Message(text="help"))
    assert response.intent.value == "help" and not response.degraded and response.sources == []
    assert "tuition for 5 credits" in response.answer and "500,000 VND" in response.answer
    assert "where is registrar" in response.answer
    assert "tuition for 12 credits" not in response.answer
    assert "500,000" in service.handle(Message(text="tuition for 1 credits")).answer
    assert "A.1" in service.handle(Message(text="where is registrar")).answer


def test_real_cli_help_question_has_answer_on_stdout_and_metadata_on_stderr(cli_environment, tmp_path):
    result = subprocess.run(
        [sys.executable, "-B", "-m", "assistant_core", "help"],
        env=cli_environment,
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
        timeout=10,
    )
    assert result.returncode == 0 and "Tuition" in result.stdout and "Office" in result.stdout
    assert json.loads(result.stderr)["intent"] == "help"
