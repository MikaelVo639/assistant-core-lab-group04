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
"""Tests for the shared exception hierarchy and its stable error codes."""

import pytest

from assistant_core.errors import (
    AssistantError,
    ConfigError,
    DataError,
    InvalidRequest,
    ProviderError,
)

ERROR_TYPES = [AssistantError, ConfigError, DataError, InvalidRequest, ProviderError]
EXPECTED_CODES = {
    AssistantError: "assistant_error",
    ConfigError: "config_error",
    DataError: "data_error",
    InvalidRequest: "invalid_request",
    ProviderError: "provider_error",
}


@pytest.mark.parametrize("error_type", ERROR_TYPES)
def test_error_code_is_stable(error_type: type[AssistantError]) -> None:
    assert error_type.code == EXPECTED_CODES[error_type]


def test_error_codes_are_unique() -> None:
    codes = [error_type.code for error_type in ERROR_TYPES]

    assert len(codes) == len(set(codes))


@pytest.mark.parametrize("error_type", ERROR_TYPES[1:])
def test_specific_errors_inherit_from_assistant_error(error_type: type[AssistantError]) -> None:
    assert issubclass(error_type, AssistantError)


@pytest.mark.parametrize("error_type", ERROR_TYPES[1:])
def test_specific_errors_can_be_caught_as_assistant_error(error_type: type[AssistantError]) -> None:
    with pytest.raises(AssistantError) as info:
        raise error_type("expected failure")

    assert info.value.code == EXPECTED_CODES[error_type]


@pytest.mark.parametrize("error_type", ERROR_TYPES)
def test_message_is_preserved(error_type: type[AssistantError]) -> None:
    error = error_type("readable detail")

    assert str(error) == "readable detail"
    assert error.args == ("readable detail",)


def test_error_without_message_has_empty_string() -> None:
    assert str(ConfigError()) == ""


def test_assistant_error_does_not_hide_unrelated_exceptions() -> None:
    with pytest.raises(ValueError):
        raise ValueError("not an assistant error")
