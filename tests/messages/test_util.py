import pytest

from wamp.messages import util, error


@pytest.mark.parametrize(
    "realm, error_message, expected_error",
    [
        (None, "error", "Realm cannot be null for "),
        (1, "error", "Realm must be of type string for "),
        ({"k": "v"}, "error", "Realm must be of type string for "),
    ],
)
def test_validate_realm_or_raise_incorrectly(realm, error_message, expected_error):
    with pytest.raises(error.InvalidRealmError) as exc_info:
        util.validate_realm_or_raise(realm, error_message)

    assert str(exc_info.value) == expected_error + error_message


def test_validate_realm_or_raise_correctly():
    realm = "realm1"
    result = util.validate_realm_or_raise(realm, "")
    assert result == realm


@pytest.mark.parametrize(
    "details, error_message, expected_error",
    [
        (None, "hello", "details must be of type dictionary for "),
        (1, "hello", "details must be of type dictionary for "),
        ({23: "v"}, "error", "Invalid type for key '23' in extra details for "),
    ],
)
def test_validate_details_or_raise_incorrectly(details, error_message, expected_error):
    with pytest.raises(error.InvalidDetails) as exc_info:
        util.validate_details_or_raise(details, error_message)

    assert str(exc_info.value) == expected_error + error_message


@pytest.mark.parametrize("details", [{}, {"authid": "mahad"}])
def test_validate_details_or_raise_correctly(details):
    result = util.validate_details_or_raise(details, "")
    assert isinstance(details, dict)
    assert result == details


@pytest.mark.parametrize(
    "session_id, error_message, expected_error",
    [
        (None, "hello", "Session ID must be an integer for "),
        (1.0, "hello", "Session ID must be an integer for "),
        ({"k": "v"}, "error", "Session ID must be an integer for "),
        (-22, "error", "Invalid Session ID value for "),
        (9007199254740993, "error", "Invalid Session ID value for "),
    ],
)
def test_validate_session_id_or_raise_incorrectly(session_id, error_message, expected_error):
    with pytest.raises(error.ProtocolError) as exc_info:
        util.validate_session_id_or_raise(session_id, error_message)

    assert str(exc_info.value) == expected_error + error_message


@pytest.mark.parametrize("session_id", [1, 30, 9007199254740992])
def test_validate_session_id_or_raise_correctly(session_id):
    result = util.validate_session_id_or_raise(session_id, "")
    assert isinstance(session_id, int)
    assert result == session_id
