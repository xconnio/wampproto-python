import pytest

from wampproto.wamp.messages import error
from wampproto.wamp.messages.goodbye import Goodbye


def test_parse_with_invalid_type():
    message = "msg"
    with pytest.raises(ValueError) as exc_info:
        Goodbye.parse(message)

    assert (
        str(exc_info.value)
        == f"invalid message type {type(message).__name__} for {Goodbye.GOODBYE_TEXT}, type should be a list"
    )


def test_parse_with_invalid_min_length():
    message = ["foo"]
    with pytest.raises(ValueError) as exc_info:
        Goodbye.parse(message)

    assert str(exc_info.value) == f"invalid message length {len(message)}, must be at least 3"


def test_parse_with_invalid_max_length():
    message = ["foo", 1, 3, 23]
    with pytest.raises(ValueError) as exc_info:
        Goodbye.parse(message)

    assert str(exc_info.value) == f"invalid message length {len(message)}, must be at most 3"


def test_parse_with_invalid_message_type():
    message = [3, {}, "wamp.close.close_realm"]
    with pytest.raises(ValueError) as exc_info:
        Goodbye.parse(message)

    assert str(exc_info.value) == f"invalid message id 3 for {Goodbye.GOODBYE_TEXT}, expected {Goodbye.MESSAGE_TYPE}"


def test_parse_with_invalid_detail_type():
    message = [6, "detail", "wamp.close.close_realm"]
    with pytest.raises(error.InvalidDetailsError) as exc_info:
        Goodbye.parse(message)

    assert str(exc_info.value) == f"details must be of type dictionary for {Goodbye.GOODBYE_TEXT}"


def test_parse_with_invalid_details_dict_key():
    message = [6, {1: "v"}, "wamp.close.close_realm"]
    with pytest.raises(error.InvalidDetailsError) as exc_info:
        Goodbye.parse(message)

    assert str(exc_info.value) == f"invalid type for key '1' in extra details for {Goodbye.GOODBYE_TEXT}"


def test_parse_with_reason_none():
    message = [6, {}, None]
    with pytest.raises(error.InvalidUriError) as exc_info:
        Goodbye.parse(message)

    assert str(exc_info.value) == f"uri cannot be null for {Goodbye.GOODBYE_TEXT}"


def test_parse_with_invalid_reason_type():
    message = [6, {}, ["wamp.close.close_realm"]]
    with pytest.raises(error.InvalidUriError) as exc_info:
        Goodbye.parse(message)

    assert str(exc_info.value) == f"uri must be of type string for {Goodbye.GOODBYE_TEXT}"


def test_parse_correctly():
    details = {"message": "The host is shutting down now."}
    reason = "wamp.close.system_shutdown"
    message = [6, details, reason]
    goodbye = Goodbye.parse(message)

    assert isinstance(goodbye, Goodbye)

    assert isinstance(goodbye.details, dict)
    assert goodbye.details == details

    assert isinstance(goodbye.reason, str)
    assert goodbye.reason == reason


def test_marshal_with_empty_details():
    reason = "wamp.close.system_shutdown"
    message = Goodbye({}, reason).marshal()

    assert isinstance(message, list)

    assert isinstance(message[0], int)
    assert message[0] == Goodbye.MESSAGE_TYPE

    assert message[1] == dict()

    assert isinstance(message[2], str)
    assert message[2] == reason


def test_marshal_with_details():
    details = {"message": "The host is shutting down now."}
    reason = "wamp.close.system_shutdown"
    message = Goodbye(details, reason).marshal()

    assert isinstance(message, list)

    assert isinstance(message[0], int)
    assert message[0] == Goodbye.MESSAGE_TYPE

    assert isinstance(message[1], dict)
    assert message[1] == details

    assert isinstance(message[2], str)
    assert message[2] == reason
