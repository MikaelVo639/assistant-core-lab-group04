"""Public request, response, and intent models for the assistant service.

These Pydantic models form the typed boundary between callers (CLI or tests)
and :class:`assistant_core.service.AssistantService`.  Validation rejects
malformed messages before any business logic runs, and the response models
keep answers, citations, and degradation state explicit.
"""

from enum import Enum

from pydantic import BaseModel, Field, field_validator

__all__ = ["Intent", "Message", "Response", "Source"]


class Intent(str, Enum):
    """Intent selected by the rule-based router for one message."""

    GREETING = "greeting"
    FEE = "fee"
    OFFICE = "office"
    RULE = "rule"
    UNKNOWN = "unknown"


class Message(BaseModel):
    """A validated user request; ``text`` is trimmed and limited to 2000 characters."""

    text: str = Field(min_length=1, max_length=2000)
    session_id: str = "local"

    @field_validator("text")
    @classmethod
    def _text_must_not_be_blank(cls, value: str) -> str:
        """Trim the message and reject whitespace-only input at the boundary."""
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("message text must not be blank")
        return cleaned


class Source(BaseModel):
    """A citation identifying the handbook rule used for an answer."""

    id: str
    title: str


class Response(BaseModel):
    """A complete answer with its intent, citations, and fallback state."""

    answer: str
    intent: Intent
    sources: list[Source] = Field(default_factory=list)
    degraded: bool = False
