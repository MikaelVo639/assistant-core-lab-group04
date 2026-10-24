"""Test-only contracts for collaborators that other members have not implemented yet.

Real modules take precedence as they become available. These substitutes allow
component tests of Minh's code; they do not prove full-package integration.
"""

import importlib
import sys
from enum import Enum
from pathlib import Path
from types import ModuleType, SimpleNamespace

from pydantic import BaseModel, Field


def install_contracts(monkeypatch) -> SimpleNamespace:
    def dependency(name: str, **members) -> ModuleType:
        fullname = f"assistant_core.{name}"
        try:
            return importlib.import_module(fullname)
        except ModuleNotFoundError as exc:
            if exc.name != fullname:
                raise
        module = ModuleType(fullname)
        module.__dict__.update(members)
        monkeypatch.setitem(sys.modules, fullname, module)
        return module

    base_error = type("AssistantError", (Exception,), {})
    errors = dependency(
        "errors",
        AssistantError=base_error,
        **{
            name: type(name, (base_error,), {})
            for name in ("ConfigError", "DataError", "InvalidRequest", "ProviderError")
        },
    )

    class Intent(str, Enum):
        GREETING = "greeting"
        FEE = "fee"
        OFFICE = "office"
        RULE = "rule"
        UNKNOWN = "unknown"

    class Message(BaseModel):
        text: str = Field(min_length=1, max_length=2000)
        session_id: str = "local"

    class Source(BaseModel):
        id: str
        title: str

    class Response(BaseModel):
        answer: str
        intent: Intent
        sources: list[Source] = Field(default_factory=list)
        degraded: bool = False

    models = dependency("models", Intent=Intent, Message=Message, Source=Source, Response=Response)

    class TemplateResponder:
        def explain(self, question, rule):
            return f"{rule.title}: {rule.text}"

    class StubLLMResponder:
        def __init__(self, fail=False):
            self.fail = fail

        def explain(self, question, rule):
            if self.fail:
                raise errors.ProviderError("simulated outage")
            return f"Based on '{rule.title}': {rule.text}"

    responder = dependency("responder", TemplateResponder=TemplateResponder, StubLLMResponder=StubLLMResponder)
    router = dependency("router", route=lambda text, names: models.Intent.RULE)

    def unconfigured_tool(*args):
        raise AssertionError("Configure the tools boundary for this component test")

    tools = dependency("tools", parse_credits=unconfigured_tool, tuition=unconfigured_tool)
    settings = SimpleNamespace(
        data_dir=Path("data"),
        llm_provider="stub",
        llm_api_key=None,
        credit_rate_vnd=450_000,
        retake_multiplier=1.5,
        max_credits=30,
        log_level="INFO",
    )
    config = dependency("config", load_settings=lambda: settings)
    office = SimpleNamespace(name="Library", room="B.201", hours="Mon-Sat 07:00-20:00")
    rule = SimpleNamespace(
        id="H26-5.3",
        title="Thesis registration",
        text=(
            "Students may register a thesis when they have at least 120 accumulated credits "
            "and a GPA of at least 2.0."
        ),
    )
    offices = SimpleNamespace(names={"library"}, find=lambda text: office)
    handbook = SimpleNamespace(search=lambda text: rule)
    knowledge = dependency(
        "knowledge",
        OfficeDirectory=SimpleNamespace(from_csv=lambda path: offices),
        Handbook=SimpleNamespace(from_json=lambda path: handbook),
    )
    logging_setup = dependency("logging_setup", setup_logging=lambda level: None)
    return SimpleNamespace(
        errors=errors,
        models=models,
        responder=responder,
        router=router,
        tools=tools,
        config=config,
        knowledge=knowledge,
        logging_setup=logging_setup,
        settings=settings,
        office=office,
        rule=rule,
        offices=offices,
        handbook=handbook,
    )
