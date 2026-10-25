"""Named exception hierarchy for the assistant service boundary.

All expected failures inherit from :class:`AssistantError`, so the CLI and the
service can handle domain errors without catching broad ``Exception``.  Every
subclass exposes a stable, machine-readable ``code`` that can be logged or
shown to callers without parsing human-readable messages.
"""

from __future__ import annotations

from typing import ClassVar

__all__ = [
    "AssistantError",
    "ConfigError",
    "DataError",
    "InvalidRequest",
    "ProviderError",
]


class AssistantError(Exception):
    """Base class for every expected assistant failure."""

    code: ClassVar[str] = "assistant_error"


class ConfigError(AssistantError):
    """Raised when configuration is missing, unreadable, or invalid."""

    code: ClassVar[str] = "config_error"


class DataError(AssistantError):
    """Raised when a knowledge file is missing or malformed."""

    code: ClassVar[str] = "data_error"


class InvalidRequest(AssistantError):
    """Raised when a user request cannot be answered as given."""

    code: ClassVar[str] = "invalid_request"


class ProviderError(AssistantError):
    """Raised when an external response provider is unavailable."""

    code: ClassVar[str] = "provider_error"
