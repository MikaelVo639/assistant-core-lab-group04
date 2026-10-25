"""Replaceable, offline response generators behind a small protocol."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from assistant_core.config import Settings
from assistant_core.errors import ConfigError, ProviderError
from assistant_core.knowledge import Rule


@runtime_checkable
class Responder(Protocol):
    """Boundary for a provider that explains an already retrieved rule."""

    def explain(self, question: str, rule: Rule) -> str:
        """Explain a rule, raising ProviderError if the provider is unavailable."""
        ...


class TemplateResponder:
    """Generate a factual answer without AI, network access, or an API key."""

    def explain(self, question: str, rule: Rule) -> str:
        """Return the handbook title and original rule text."""
        return f"{rule.title}: {rule.text}"


class StubLLMResponder:
    """Deterministic provider substitute with an explicit outage switch for tests."""

    def __init__(self, fail: bool = False) -> None:
        self.fail = fail

    def explain(self, question: str, rule: Rule) -> str:
        """Return a stable answer or simulate a named provider failure."""
        if self.fail:
            raise ProviderError("stub provider unavailable")
        return f"Based on '{rule.title}': {rule.text}"


def make_responder(settings: Settings) -> Responder:
    """Build the configured provider; only the offline stub is supported."""
    if settings.llm_provider == "stub":
        return StubLLMResponder()
    raise ConfigError(f"unsupported LLM_PROVIDER: {settings.llm_provider!r}")
    """Select an offline responder from validated settings."""
    if settings.llm_provider == "stub":
        return StubLLMResponder()
    if settings.llm_provider == "template":
        return TemplateResponder()
    raise ConfigError(f"Unsupported LLM provider: {settings.llm_provider}")
