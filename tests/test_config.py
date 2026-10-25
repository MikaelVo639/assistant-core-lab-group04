"""Tests for environment-backed, immutable configuration."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from assistant_core.config import Settings, load_settings
from assistant_core.errors import ConfigError


def test_defaults_when_no_env_file(tmp_path: Path) -> None:
    settings = load_settings(env_file=tmp_path / "missing.env", environ={})

    assert settings.data_dir == Path("data")
    assert settings.llm_provider == "stub"
    assert settings.llm_api_key is None
    assert settings.credit_rate_vnd == 450_000
    assert settings.retake_multiplier == 1.5
    assert settings.max_credits == 30
    assert settings.log_level == "INFO"


def test_dotenv_is_read_and_normalised(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text(
        "ASSISTANT_DATA_DIR=fixtures\n"
        "LLM_PROVIDER=Template\n"
        "CREDIT_RATE_VND=500000\n"
        "RETAKE_MULTIPLIER=2\n"
        "MAX_CREDITS=24\n"
        "LOG_LEVEL=debug\n",
        encoding="utf-8",
    )

    settings = load_settings(env_file=env_file, environ={})

    assert settings.data_dir == Path("fixtures")
    assert settings.llm_provider == "template"
    assert settings.credit_rate_vnd == 500_000
    assert settings.retake_multiplier == 2.0
    assert settings.max_credits == 24
    assert settings.log_level == "DEBUG"


def test_process_environment_overrides_dotenv(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("CREDIT_RATE_VND=500000\n", encoding="utf-8")

    settings = load_settings(env_file=env_file, environ={"CREDIT_RATE_VND": "600000"})

    assert settings.credit_rate_vnd == 600_000


def test_empty_values_fall_back_to_defaults(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("MAX_CREDITS=\nLLM_API_KEY=\n", encoding="utf-8")

    settings = load_settings(env_file=env_file, environ={})

    assert settings.max_credits == 30
    assert settings.llm_api_key is None


def test_invalid_value_raises_config_error_without_echoing_it(tmp_path: Path) -> None:
    env_file = tmp_path / ".env"
    env_file.write_text("CREDIT_RATE_VND=not-a-number\n", encoding="utf-8")

    with pytest.raises(ConfigError) as info:
        load_settings(env_file=env_file, environ={})

    message = str(info.value)
    assert "CREDIT_RATE_VND" in message
    assert "not-a-number" not in message


def test_unknown_provider_is_rejected() -> None:
    with pytest.raises(ConfigError, match="LLM_PROVIDER"):
        load_settings(env_file=None, environ={"LLM_PROVIDER": "openai"})


def test_api_key_is_hidden_from_repr() -> None:
    settings = Settings(llm_api_key="sk-secret-value")

    assert "sk-secret-value" not in repr(settings)


def test_settings_are_immutable() -> None:
    settings = Settings()

    with pytest.raises(ValidationError):
        settings.credit_rate_vnd = 1  # type: ignore[misc]


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("credit_rate_vnd", 0),
        ("credit_rate_vnd", -1),
        ("retake_multiplier", -0.5),
        ("max_credits", 0),
        ("log_level", "TRACE"),
    ],
)
def test_out_of_range_settings_are_rejected(field: str, value: object) -> None:
    with pytest.raises(ValidationError):
        Settings(**{field: value})


def test_api_key_is_excluded_from_dumps() -> None:
    settings = Settings(llm_api_key="sk-secret-value")

    assert "llm_api_key" not in settings.model_dump()
