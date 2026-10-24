from pathlib import Path

import pytest

from assistant_core.config import MappingSource, Settings, SettingsLoader, load_settings
from assistant_core.errors import ConfigError


def load(**env: str) -> Settings:
    return SettingsLoader(MappingSource(env)).load()


def test_defaults():
    s = load()
    assert s.llm_provider == "stub" and s.max_credits == 30 and s.data_dir == Path("data")


def test_values_are_parsed_from_strings():
    s = load(CREDIT_RATE_VND="500000", RETAKE_MULTIPLIER="2", LOG_LEVEL="debug", ASSISTANT_DATA_DIR="x")
    assert (s.credit_rate_vnd, s.retake_multiplier, s.log_level, s.data_dir) == (500000, 2.0, "DEBUG", Path("x"))


def test_empty_value_means_unset():
    assert load(MAX_CREDITS="").max_credits == 30


def test_real_provider_requires_key():
    with pytest.raises(ConfigError, match="LLM_API_KEY"):
        load(LLM_PROVIDER="openai")


def test_key_not_in_repr_or_errors():
    assert "sekret" not in repr(load(LLM_PROVIDER="openai", LLM_API_KEY="sekret"))
    with pytest.raises(ConfigError) as ei:
        load(LLM_PROVIDER="openai", LLM_API_KEY="sekret", MAX_CREDITS="abc")
    assert "sekret" not in str(ei.value)


@pytest.mark.parametrize(
    ("var", "value"),
    [
        ("MAX_CREDITS", "abc"),
        ("MAX_CREDITS", "0"),
        ("CREDIT_RATE_VND", "-1"),
        ("RETAKE_MULTIPLIER", "-0.5"),
        ("LOG_LEVEL", "LOUD"),
    ],
)
def test_invalid_values_raise_config_error(var, value):
    with pytest.raises(ConfigError, match=var):
        load(**{var: value})


def test_settings_are_immutable():
    with pytest.raises(ValueError):
        load().max_credits = 99


def test_env_file_is_read_and_real_env_wins(tmp_path, monkeypatch):
    f = tmp_path / ".env"
    f.write_text("MAX_CREDITS=12\nCREDIT_RATE_VND=1000\n", encoding="utf-8")
    monkeypatch.delenv("MAX_CREDITS", raising=False)
    monkeypatch.setenv("CREDIT_RATE_VND", "2000")
    s = load_settings(str(f))
    assert s.max_credits == 12 and s.credit_rate_vnd == 2000


def test_load_settings_does_not_mutate_environ(tmp_path, monkeypatch):
    import os

    f = tmp_path / ".env"
    f.write_text("MAX_CREDITS=12\n", encoding="utf-8")
    monkeypatch.delenv("MAX_CREDITS", raising=False)
    load_settings(str(f))
    assert "MAX_CREDITS" not in os.environ
