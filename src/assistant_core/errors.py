class AssistantError(Exception):
    """Base exception for assistant-core errors."""


class ConfigError(AssistantError):
    """Raised when environment or settings are missing or invalid."""


class DataError(AssistantError):
    """Raised when data files are missing or unparseable."""


class InvalidRequest(AssistantError):
    """Raised when a user request is invalid or cannot be fulfilled."""


class ProviderError(AssistantError):
    """Raised when an external LLM provider fails."""
