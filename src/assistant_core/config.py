"""Read validated configuration without exposing provider credentials."""

import os
from pathlib import Path
from typing import Literal

from dotenv import dotenv_values
from pydantic import BaseModel, Field, ValidationError, model_validator

from assistant_core.errors import ConfigError


class Settings(BaseModel):
    """Runtime settings supplied to the service rather than stored in domain globals."""

    data_dir: Path = Path("data")
    llm_provider: str = Field(default="stub", min_length=1)
    llm_api_key: str | None = Field(default=None, repr=False, exclude=True)
    credit_rate_vnd: int = Field(default=450_000, gt=0)
    retake_multiplier: float = Field(default=1.5, gt=0, allow_inf_nan=False)
    max_credits: int = Field(default=30, ge=1)
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    @model_validator(mode="after")
    def require_provider_key(self) -> "Settings":
        """Require credentials for future providers, while allowing an offline stub."""
        if self.llm_provider != "stub" and not self.llm_api_key:
            raise ValueError("A non-stub provider requires an API key")
        return self


def load_settings(env_file: str | None = ".env") -> Settings:
    """Overlay shell variables on an optional dotenv file without mutating the shell."""
    try:
        values = dotenv_values(env_file) if env_file else {}

        def value(name: str, default: str) -> str:
            return os.environ.get(name, values.get(name) or default)

        return Settings(
            data_dir=Path(value("ASSISTANT_DATA_DIR", "data")),
            llm_provider=value("LLM_PROVIDER", "stub"),
            llm_api_key=value("LLM_API_KEY", "") or None,
            credit_rate_vnd=value("CREDIT_RATE_VND", "450000"),
            retake_multiplier=value("RETAKE_MULTIPLIER", "1.5"),
            max_credits=value("MAX_CREDITS", "30"),
            log_level=value("LOG_LEVEL", "INFO").upper(),
        )
    except (ValidationError, OSError, UnicodeError):
        raise ConfigError("Invalid assistant configuration; check environment settings.") from None
