"""Validate environment settings without leaking provider credentials."""

import importlib

import pytest

from assistant_core.errors import ConfigError


@pytest.fixture
def config():
    return importlib.import_module("assistant_core.config")


@pytest.fixture(autouse=True)
def isolated_environment(monkeypatch):
    for name in (
        "ASSISTANT_DATA_DIR",
        "LLM_PROVIDER",
        "LLM_API_KEY",
        "CREDIT_RATE_VND",
        "RETAKE_MULTIPLIER",
        "MAX_CREDITS",
        "LOG_LEVEL",
    ):
        monkeypatch.delenv(name, raising=False)


def test_defaults_and_shell_over_dotenv(config, monkeypatch, tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("CREDIT_RATE_VND=600000\nMAX_CREDITS=20\n", encoding="utf-8")
    monkeypatch.setenv("CREDIT_RATE_VND", "500000")
    settings = config.load_settings(str(env_file))
    assert settings.credit_rate_vnd == 500_000 and settings.max_credits == 20
    assert settings.llm_provider == "stub" and settings.retake_multiplier == 1.5


@pytest.mark.parametrize(
    "name,value",
    [
        ("CREDIT_RATE_VND", "bad"),
        ("CREDIT_RATE_VND", "0"),
        ("MAX_CREDITS", "-1"),
        ("RETAKE_MULTIPLIER", "nan"),
        ("RETAKE_MULTIPLIER", "-2"),
        ("LOG_LEVEL", "unrecognised"),
    ],
)
def test_invalid_environment_raises_named_error(config, monkeypatch, name, value):
    monkeypatch.setenv(name, value)
    with pytest.raises(ConfigError):
        config.load_settings(None)


def test_unknown_provider_is_rejected_even_with_a_key(config, monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "future-provider")
    with pytest.raises(ConfigError):
        config.load_settings(None)
    monkeypatch.setenv("LLM_API_KEY", "private-example-key")
    with pytest.raises(ConfigError):
        config.load_settings(None)
    monkeypatch.setenv("LLM_PROVIDER", "template")
    settings = config.load_settings(None)
    assert settings.llm_api_key == "private-example-key"
    assert "private-example-key" not in repr(settings)
    assert "llm_api_key" not in settings.model_dump()


def test_error_does_not_include_sensitive_environment_values(config, monkeypatch):
    monkeypatch.setenv("CREDIT_RATE_VND", "private-example-key")
    with pytest.raises(ConfigError) as failure:
        config.load_settings(None)
    assert "private-example-key" not in str(failure.value)


def test_invalid_dotenv_encoding_is_a_safe_named_error(config, tmp_path):
    path = tmp_path / ".env"
    path.write_bytes(b"CREDIT_RATE_VND=\xff\n")
    with pytest.raises(ConfigError):
        config.load_settings(str(path))
