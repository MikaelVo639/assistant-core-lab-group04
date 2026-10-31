"""Configuration (Twelve-Factor III): settings come from the environment, never from code.

Design:
- ``Settings``       immutable value object; owns all validation (types, ranges, normalisation).
- ``ConfigSource``   strategy for where raw values come from (process env, ``.env`` file, a dict in tests).
- ``SettingsLoader`` factory that maps env var names to fields and turns validation failures into ``ConfigError``.
- ``load_settings``  facade kept for callers that just want the default behaviour.
"""

from __future__ import annotations

import os
from collections.abc import Mapping
from pathlib import Path
from typing import Literal, Protocol

from dotenv import dotenv_values
from pydantic import BaseModel, ConfigDict, Field, ValidationError, field_validator

from assistant_core.errors import ConfigError

LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
ProviderName = Literal["stub", "template"]


class Settings(BaseModel):
    """Validated, immutable settings passed to the service at startup."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    data_dir: Path = Path("data")
    llm_provider: ProviderName = "stub"
    llm_api_key: str | None = Field(default=None, repr=False, exclude=True)  # never printed or dumped
    credit_rate_vnd: int = Field(default=450_000, gt=0)
    retake_multiplier: float = Field(default=1.5, ge=0, allow_inf_nan=False)
    max_credits: int = Field(default=30, ge=1)
    log_level: LogLevel = "INFO"
    api_admin_key: str | None = Field(default=None, repr=False, exclude=True)  # never printed or dumped
    weather_url: str = "https://api.open-meteo.com/v1/forecast"
    weather_timeout_s: float = Field(default=3.0, gt=0, allow_inf_nan=False)
    campus_lat: float = Field(default=10.7626, ge=-90, le=90)
    campus_lon: float = Field(default=106.6822, ge=-180, le=180)
    rate_limit_per_min: int = Field(default=30, ge=1)

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

    @field_validator("llm_api_key", "api_admin_key", mode="before")
    @classmethod
    def _clean_api_key(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip() or None
        return value

    @field_validator("log_level", mode="before")
    @classmethod
    def _clean_log_level(cls, value: object) -> object:
        return value.strip().upper() if isinstance(value, str) else value


class ConfigSource(Protocol):
    def get(self, name: str) -> str | None: ...


class MappingSource:
    """Reads from any mapping; the base for the sources below and handy in tests."""

    def __init__(self, values: Mapping[str, str | None]) -> None:
        self._values = values

    def get(self, name: str) -> str | None:
        return self._values.get(name)


class EnvSource(MappingSource):
    """Process environment, optionally layered over a ``.env`` file (real env vars win).

    The file is parsed, not exported, so loading never mutates ``os.environ``.
    """

    def __init__(self, env_file: str | Path | None = ".env", environ: Mapping[str, str] | None = None) -> None:
        file_values: Mapping[str, str | None] = {}
        if env_file is not None:
            try:
                file_values = dotenv_values(env_file)
            except (OSError, UnicodeError) as e:
                raise ConfigError(f"Could not read configuration file: {env_file}") from e
        process_env = os.environ if environ is None else environ
        nonblank_process = {name: value for name, value in process_env.items() if value.strip()}
        super().__init__({**file_values, **nonblank_process})


class SettingsLoader:
    ENV_VARS = {
        "data_dir": "ASSISTANT_DATA_DIR",
        "llm_provider": "LLM_PROVIDER",
        "llm_api_key": "LLM_API_KEY",
        "credit_rate_vnd": "CREDIT_RATE_VND",
        "retake_multiplier": "RETAKE_MULTIPLIER",
        "max_credits": "MAX_CREDITS",
        "log_level": "LOG_LEVEL",
        "api_admin_key": "API_ADMIN_KEY",
        "weather_url": "WEATHER_URL",
        "weather_timeout_s": "WEATHER_TIMEOUT_S",
        "campus_lat": "CAMPUS_LAT",
        "campus_lon": "CAMPUS_LON",
        "rate_limit_per_min": "RATE_LIMIT_PER_MIN",
    }

    def __init__(self, source: ConfigSource) -> None:
        self._source = source

    def load(self) -> Settings:
        raw = {field: self._source.get(var) for field, var in self.ENV_VARS.items()}
        present = {field: value for field, value in raw.items() if value and value.strip()}  # blank == unset
        try:
            return Settings(**present)
        except ValidationError as e:
            # Report names and reasons only, and drop the cause: error inputs could contain the API keys.
            problems = "; ".join(
                f"{self.ENV_VARS.get(str(err['loc'][0]), 'settings') if err['loc'] else 'settings'}: {err['msg']}"
                for err in e.errors()
            )
            raise ConfigError(f"invalid configuration: {problems}") from None


def load_settings(env_file: str | Path | None = ".env", environ: Mapping[str, str] | None = None) -> Settings:
    return SettingsLoader(EnvSource(env_file, environ)).load()
