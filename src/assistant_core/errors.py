"""Exception hierarchy for assistant_core.

Callers catch ``AssistantError`` to handle any domain failure, or a subclass to
handle one category. Each subclass carries a stable machine-readable ``code``
so logs and the CLI can report the category without parsing messages.
"""


class AssistantError(Exception):
    """Base class for all assistant errors."""

    code = "assistant_error"


class ConfigError(AssistantError):
    """Configuration is missing or invalid."""

    code = "config_error"


class DataError(AssistantError):
    """A knowledge file is missing or malformed."""

    code = "data_error"


class InvalidRequest(AssistantError):
    """The user's request cannot be processed as given."""

    code = "invalid_request"


class ProviderError(AssistantError):
    """The AI provider failed (timeout, outage, bad response)."""

    code = "provider_error"
