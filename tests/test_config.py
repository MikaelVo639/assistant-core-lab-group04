import pytest

from assistant_core.config import load_settings
from assistant_core.errors import ConfigError


def test_defaults(monkeypatch):
    for k in ("LLM_PROVIDER", "LLM_API_KEY", "MAX_CREDITS"):
        monkeypatch.delenv(k, raising=False)
    s = load_settings(env_file=None)
    assert s.llm_provider == "stub" and s.max_credits == 30


def test_real_provider_requires_key(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.delenv("LLM_API_KEY", raising=False)
    with pytest.raises(ConfigError):
        load_settings(env_file=None)


def test_key_not_in_repr(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("LLM_API_KEY", "sekret")
    assert "sekret" not in repr(load_settings(env_file=None))


def test_bad_number_is_config_error(monkeypatch):
    monkeypatch.setenv("MAX_CREDITS", "abc")
    with pytest.raises(ConfigError):
        load_settings(env_file=None)
