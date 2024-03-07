import pytest

from wamp.messages import error
from wamp.messages.abort import Abort


def test_parse_with_invalid_type():
    message = "msg"
    with pytest.raises(error.ProtocolError) as exc_info:
        Abort.parse(message)

    assert (
        str(exc_info.value) == f"invalid message type '{type(message)}' for {Abort.ABORT_TEXT}, type should be a list"
    )


def test_parse_with_invalid_list_length():
    message = ["foo"]
    with pytest.raises(error.ProtocolError) as exc_info:
        Abort.parse(message)

    assert (
        str(exc_info.value) == f"invalid message length '{len(message)}' for {Abort.ABORT_TEXT}, "
        f"length should be equal to three"
    )


def test_parse_with_invalid_message_type():
    message = [2, {}, "wamp.error.no_such_realm"]
    with pytest.raises(error.ProtocolError) as exc_info:
        Abort.parse(message)

    assert str(exc_info.value) == f"invalid message type for {Abort.ABORT_TEXT}"


def test_parse_with_invalid_detail_type():
    message = [3, "detail", "wamp.error.no_such_realm"]
    with pytest.raises(error.InvalidDetailsError) as exc_info:
        Abort.parse(message)

    assert str(exc_info.value) == f"details must be of type dictionary for {Abort.ABORT_TEXT}"


def test_parse_with_invalid_details_dict_key():
    message = [3, {1: "v"}, "wamp.error.no_such_realm"]
    with pytest.raises(error.InvalidDetailsError) as exc_info:
        Abort.parse(message)

    assert str(exc_info.value) == f"invalid type for key '1' in extra details for {Abort.ABORT_TEXT}"


def test_parse_with_reason_none():
    message = [3, {}, None]
    with pytest.raises(error.InvalidUriError) as exc_info:
        Abort.parse(message)

    assert str(exc_info.value) == f"uri cannot be null for {Abort.ABORT_TEXT}"


def test_parse_with_invalid_reason_type():
    message = [3, {}, ["wamp.error.no_such_realm"]]
    with pytest.raises(error.InvalidUriError) as exc_info:
        Abort.parse(message)

    assert str(exc_info.value) == f"uri must be of type string for {Abort.ABORT_TEXT}"


def test_parse_correctly():
    details = {"message": "The realm does not exist."}
    reason = "wamp.error.no_such_realm"
    message = [3, details, reason]
    abort = Abort.parse(message)

    assert isinstance(abort, Abort)

    assert isinstance(abort.details, dict)
    assert abort.details == details

    assert isinstance(abort.reason, str)
    assert abort.reason == reason


def test_marshal_with_empty_details():
    reason = "wamp.error.no_such_realm"
    message = Abort({}, reason).marshal()

    assert isinstance(message, list)

    assert isinstance(message[0], int)
    assert message[0] == Abort.MESSAGE_TYPE

    assert message[1] == dict()

    assert isinstance(message[2], str)
    assert message[2] == reason


def test_marshal_with_details():
    details = {"message": "The realm does not exist."}
    reason = "wamp.error.no_such_realm"
    message = Abort(details, reason).marshal()

    assert isinstance(message, list)

    assert isinstance(message[0], int)
    assert message[0] == Abort.MESSAGE_TYPE

    assert isinstance(message[1], dict)
    assert message[1] == details

    assert isinstance(message[2], str)
    assert message[2] == reason
