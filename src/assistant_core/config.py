"""Configuration (Twelve-Factor III): settings come from the environment, never from code.

Design:
- ``Settings``       immutable value object; owns all validation (types, ranges, cross-field rules).
- ``ConfigSource``   strategy for where raw values come from (process env, ``.env`` file, a dict in tests).
- ``SettingsLoader`` factory that maps env var names to fields and turns validation failures into ``ConfigError``.
- ``load_settings``  facade kept for callers that just want the default behaviour.
"""
"""Load and validate runtime settings from environment variables and ``.env``."""

from __future__ import annotations

import os
from collections.abc import Mapping
from pathlib import Path
from typing import Literal, Protocol

from dotenv import dotenv_values
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator, model_validator
from typing import Literal

from dotenv import dotenv_values
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

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
ProviderName = Literal["stub", "template"]

ENV_TO_FIELD = {
    "ASSISTANT_DATA_DIR": "data_dir",
    "LLM_PROVIDER": "llm_provider",
    "LLM_API_KEY": "llm_api_key",
    "CREDIT_RATE_VND": "credit_rate_vnd",
    "RETAKE_MULTIPLIER": "retake_multiplier",
    "MAX_CREDITS": "max_credits",
    "LOG_LEVEL": "log_level",
}
FIELD_TO_ENV = {field: name for name, field in ENV_TO_FIELD.items()}


class Settings(BaseModel):
    """Validated, immutable settings passed to the service at startup."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    data_dir: Path = Path("data")
    llm_provider: ProviderName = "stub"
    llm_api_key: str | None = Field(default=None, repr=False, exclude=True)
    credit_rate_vnd: int = Field(default=450_000, gt=0)
    retake_multiplier: float = Field(default=1.5, ge=0, allow_inf_nan=False)
    max_credits: int = Field(default=30, ge=1)
    log_level: LogLevel = "INFO"

    @field_validator("data_dir", mode="before")
    @classmethod
    def _clean_data_dir(cls, value: object) -> object:
        if isinstance(value, str):
            return Path(value.strip() or "data")
        return value

    @field_validator("llm_provider", mode="before")
    @classmethod
    def _clean_provider(cls, value: object) -> object:
        return value.strip().lower() if isinstance(value, str) else value

    @field_validator("llm_api_key", mode="before")
    @classmethod
    def _clean_api_key(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip() or None
        return value

    @field_validator("log_level", mode="before")
    @classmethod
    def _clean_log_level(cls, value: object) -> object:
        return value.strip().upper() if isinstance(value, str) else value


def _read_dotenv(env_file: str | Path | None) -> Mapping[str, str | None]:
    """Read a dotenv file without mutating ``os.environ``."""
    if env_file is None:
        return {}
    try:
        return dotenv_values(env_file)
    except (OSError, UnicodeError) as exc:
        raise ConfigError(f"Could not read configuration file: {env_file}") from exc


def _pick(
    process_env: Mapping[str, str | None],
    file_values: Mapping[str, str | None],
    name: str,
    default: str,
) -> str:
    """Return the first non-empty value: process env, dotenv, then default."""
    for candidate in (process_env.get(name), file_values.get(name)):
        if candidate is not None and candidate.strip():
            return candidate
    return default


def _build_payload(
    process_env: Mapping[str, str | None],
    file_values: Mapping[str, str | None],
) -> dict[str, str]:
    """Map the documented environment variables to settings fields."""
    return {
        "data_dir": _pick(process_env, file_values, "ASSISTANT_DATA_DIR", "data"),
        "llm_provider": _pick(process_env, file_values, "LLM_PROVIDER", "stub"),
        "llm_api_key": _pick(process_env, file_values, "LLM_API_KEY", ""),
        "credit_rate_vnd": _pick(process_env, file_values, "CREDIT_RATE_VND", "450000"),
        "retake_multiplier": _pick(process_env, file_values, "RETAKE_MULTIPLIER", "1.5"),
        "max_credits": _pick(process_env, file_values, "MAX_CREDITS", "30"),
        "log_level": _pick(process_env, file_values, "LOG_LEVEL", "INFO"),
    }


def load_settings(
    env_file: str | Path | None = ".env",
    environ: Mapping[str, str] | None = None,
) -> Settings:
    """Build settings from process environment over an optional dotenv file.

    Real environment variables take precedence over values in ``env_file``.
    An empty value is treated as "not provided" so the documented default is
    used.  Validation errors name the offending environment variable but never
    echo its value, which keeps secrets out of startup logs.
    """
    process_env = os.environ if environ is None else environ
    payload = _build_payload(process_env, _read_dotenv(env_file))

    try:
        return Settings(**payload)
    except ValidationError as exc:
        fields = sorted({str(error["loc"][0]) for error in exc.errors() if error["loc"]})
        names = ", ".join(FIELD_TO_ENV.get(field, field) for field in fields) or "unknown"
        raise ConfigError(f"Invalid configuration for: {names}") from None
