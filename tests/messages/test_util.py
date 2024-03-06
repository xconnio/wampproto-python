import pytest

from wamp.messages import util, error


def test_validate_realm_or_raise_with_realm_none():
    error_message = "error"
    with pytest.raises(error.InvalidRealmError) as exc_info:
        util.validate_realm_or_raise(None, error_message)

    assert str(exc_info.value) == f"realm cannot be null for {error_message}"


def test_validate_realm_or_raise_with_invalid_realm_type():
    error_message = "error"
    with pytest.raises(error.InvalidRealmError) as exc_info:
        util.validate_realm_or_raise(1, error_message)

    assert str(exc_info.value) == f"realm must be of type string for {error_message}"


def test_validate_realm_or_raise_correctly():
    realm = "realm1"
    result = util.validate_realm_or_raise(realm, "")
    assert result == realm


def test_validate_details_or_raise_with_invalid_detail_type():
    error_message = "Ping"
    with pytest.raises(error.InvalidDetailsError) as exc_info:
        util.validate_details_or_raise(["detail"], error_message)

    assert str(exc_info.value) == f"details must be of type dictionary for {error_message}"


def test_validate_details_or_raise_with_invalid_detail_key_type():
    error_message = "Ping"
    with pytest.raises(error.InvalidDetailsError) as exc_info:
        util.validate_details_or_raise({23: "v"}, error_message)

    assert str(exc_info.value) == f"invalid type for key '23' in extra details for {error_message}"


@pytest.mark.parametrize("details", [{}, {"authid": "mahad"}])
def test_validate_details_or_raise_correctly(details):
    result = util.validate_details_or_raise(details, "")
    assert isinstance(details, dict)
    assert result == details


def test_validate_session_id_or_raise_with_invalid_session_type():
    error_message = "Pong"
    invalid_values = [None, 1.0, {"k": "v"}]
    for session_id in invalid_values:
        with pytest.raises(error.ProtocolError) as exc_info:
            util.validate_session_id_or_raise(session_id, error_message)

        assert str(exc_info.value) == f"session ID must be an integer for {error_message}"


def test_validate_session_id_or_raise_with_out_of_range_session_id():
    error_message = "Pong"
    invalid_values = [-10, 9007199254740993]
    for session_id in invalid_values:
        with pytest.raises(error.ProtocolError) as exc_info:
            util.validate_session_id_or_raise(session_id, error_message)

        assert str(exc_info.value) == f"invalid Session ID value for {error_message}"


@pytest.mark.parametrize("session_id", [1, 30, 9007199254740992])
def test_validate_session_id_or_raise_correctly(session_id):
    result = util.validate_session_id_or_raise(session_id, "")
    assert isinstance(session_id, int)
    assert result == session_id
