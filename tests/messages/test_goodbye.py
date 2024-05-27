import pytest

from wampproto.messages import util
from wampproto.messages.goodbye import Goodbye, GoodbyeFields


def test_parse_with_invalid_type():
    message = "msg"
    with pytest.raises(ValueError) as exc_info:
        Goodbye.parse(message)

    assert (
        str(exc_info.value)
        == f"invalid message type {type(message).__name__} for {Goodbye.TEXT}, type should be a list"
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

    assert str(exc_info.value) == f"invalid message id 3 for {Goodbye.TEXT}, expected {Goodbye.TYPE}"


def test_parse_with_invalid_detail_type():
    message = [6, "detail", "wamp.close.close_realm"]
    with pytest.raises(ValueError) as exc_info:
        Goodbye.parse(message)

    assert str(exc_info.value) == f"{Goodbye.TEXT}: value at index 1 must be of type '{util.DICT}' but was str"


def test_parse_with_reason_none():
    message = [6, {}, None]
    with pytest.raises(ValueError) as exc_info:
        Goodbye.parse(message)

    assert str(exc_info.value) == f"{Goodbye.TEXT}: value at index 2 must be of type '{util.STRING}' but was NoneType"


def test_parse_with_invalid_reason_type():
    message = [6, {}, ["wamp.close.close_realm"]]
    with pytest.raises(ValueError) as exc_info:
        Goodbye.parse(message)

    assert str(exc_info.value) == f"{Goodbye.TEXT}: value at index 2 must be of type '{util.STRING}' but was list"


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
    message = Goodbye(GoodbyeFields({}, reason)).marshal()

    assert isinstance(message, list)

    assert isinstance(message[0], int)
    assert message[0] == Goodbye.TYPE

    assert message[1] == dict()

    assert isinstance(message[2], str)
    assert message[2] == reason


def test_marshal_with_details():
    details = {"message": "The host is shutting down now."}
    reason = "wamp.close.system_shutdown"
    message = Goodbye(GoodbyeFields(details, reason)).marshal()

    assert isinstance(message, list)

    assert isinstance(message[0], int)
    assert message[0] == Goodbye.TYPE

    assert isinstance(message[1], dict)
    assert message[1] == details

    assert isinstance(message[2], str)
    assert message[2] == reason
