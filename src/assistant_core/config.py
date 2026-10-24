"""Configuration (Twelve-Factor III): settings come from the environment, never from code.

Design:
- ``Settings``       immutable value object; owns all validation (types, ranges, cross-field rules).
- ``ConfigSource``   strategy for where raw values come from (process env, ``.env`` file, a dict in tests).
- ``SettingsLoader`` factory that maps env var names to fields and turns validation failures into ``ConfigError``.
- ``load_settings``  facade kept for callers that just want the default behaviour.
"""

import os
from collections.abc import Mapping
from pathlib import Path
from typing import Literal, Protocol

from dotenv import dotenv_values
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator, model_validator

from assistant_core.errors import ConfigError

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class Settings(BaseModel):
    model_config = ConfigDict(frozen=True)

    data_dir: Path = Path("data")
    llm_provider: str = "stub"
    llm_api_key: str | None = Field(default=None, repr=False)  # never printed
    credit_rate_vnd: int = Field(default=450_000, gt=0)
    retake_multiplier: float = Field(default=1.5, ge=0)
    max_credits: int = Field(default=30, gt=0)
    log_level: LogLevel = "INFO"

    @field_validator("log_level", mode="before")
    @classmethod
    def _normalise_log_level(cls, v: object) -> object:
        return v.upper() if isinstance(v, str) else v

    @model_validator(mode="after")
    def _real_provider_needs_key(self) -> "Settings":
        if self.llm_provider != "stub" and not self.llm_api_key:
            raise ValueError(f"LLM_API_KEY is required when LLM_PROVIDER={self.llm_provider!r}")
        return self


class ConfigSource(Protocol):
    def get(self, name: str) -> str | None: ...


class MappingSource:
    """Reads from any mapping; the base for the sources below and handy in tests."""

    def __init__(self, values: Mapping[str, str]) -> None:
        self._values = values

    def get(self, name: str) -> str | None:
        return self._values.get(name)


class EnvSource(MappingSource):
    """Process environment, optionally layered over a ``.env`` file (real env vars win).

    The file is parsed, not exported, so loading never mutates ``os.environ``.
    """

    def __init__(self, env_file: str | None = ".env") -> None:
        file_values = {k: v for k, v in dotenv_values(env_file).items() if v is not None} if env_file else {}
        super().__init__({**file_values, **os.environ})


class SettingsLoader:
    ENV_VARS = {
        "data_dir": "ASSISTANT_DATA_DIR",
        "llm_provider": "LLM_PROVIDER",
        "llm_api_key": "LLM_API_KEY",
        "credit_rate_vnd": "CREDIT_RATE_VND",
        "retake_multiplier": "RETAKE_MULTIPLIER",
        "max_credits": "MAX_CREDITS",
        "log_level": "LOG_LEVEL",
    }

    def __init__(self, source: ConfigSource) -> None:
        self._source = source

    def load(self) -> Settings:
        raw = {field: self._source.get(var) for field, var in self.ENV_VARS.items()}
        present = {field: value for field, value in raw.items() if value}  # empty string == unset
        try:
            return Settings(**present)
        except ValidationError as e:
            # Report names and reasons only: error input values could contain the API key.
            problems = "; ".join(
                f"{self.ENV_VARS.get(str(err['loc'][0]), 'settings') if err['loc'] else 'settings'}: {err['msg']}"
                for err in e.errors()
            )
            raise ConfigError(f"invalid configuration: {problems}") from e


def load_settings(env_file: str | None = ".env") -> Settings:
    return SettingsLoader(EnvSource(env_file)).load()
