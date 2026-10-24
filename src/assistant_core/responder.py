from typing import Protocol

from assistant_core.config import Settings
from assistant_core.errors import ConfigError, ProviderError
from assistant_core.knowledge import Rule


class Responder(Protocol):
    def respond(self, question: str, rule: Rule) -> str: ...


class TemplateResponder:
    """Deterministic answer straight from the rule; also the fallback when a provider fails."""

    def respond(self, question: str, rule: Rule) -> str:
        return rule.format_fallback_response()


class StubProvider:
    """Offline stand-in for an LLM; `fail=True` simulates an outage."""

    def __init__(self, fail: bool = False) -> None:
        self.fail = fail

    def respond(self, question: str, rule: Rule) -> str:
        if self.fail:
            raise ProviderError("stub provider failure")
        prompt = f"Answer using this rule: {rule.text} Question: {question}"
        return f"Here is what I found: {prompt[-120:]} (source: {rule.id})"


def make_responder(settings: Settings) -> Responder:
    if settings.llm_provider == "stub":
        return StubProvider()
    raise ConfigError(f"unsupported LLM_PROVIDER: {settings.llm_provider!r}")
