import pytest

from assistant_core.errors import AssistantError, ConfigError, DataError, InvalidRequest, ProviderError

SUBCLASSES = [ConfigError, DataError, InvalidRequest, ProviderError]


@pytest.mark.parametrize("cls", SUBCLASSES)
def test_subclass_is_assistant_error(cls):
    with pytest.raises(AssistantError):
        raise cls("boom")


def test_codes_are_unique_and_stable():
    codes = [c.code for c in [AssistantError, *SUBCLASSES]]
    assert len(set(codes)) == len(codes)
    assert ConfigError.code == "config_error"


def test_message_preserved():
    assert str(DataError("bad file")) == "bad file"
