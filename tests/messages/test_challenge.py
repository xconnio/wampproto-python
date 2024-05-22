import pytest

from wampproto.messages import exceptions, util
from wampproto.messages.challenge import Challenge


def test_parse_with_invalid_type():
    message = "msg"
    with pytest.raises(ValueError) as exc_info:
        Challenge.parse(message)

    assert (
        str(exc_info.value)
        == f"invalid message type {type(message).__name__} for {Challenge.TEXT}, type should be a list"
    )


def test_parse_with_invalid_min_length():
    message = [1]
    with pytest.raises(ValueError) as exc_info:
        Challenge.parse(message)

    assert str(exc_info.value) == f"invalid message length {len(message)}, must be at least 3"


def test_parse_with_invalid_max_length():
    message = [1, 3, 4, 5]
    with pytest.raises(ValueError) as exc_info:
        Challenge.parse(message)

    assert str(exc_info.value) == f"invalid message length {len(message)}, must be at most 3"


def test_parse_with_invalid_message_type():
    message = [2, "anonymous", {}]
    with pytest.raises(ValueError) as exc_info:
        Challenge.parse(message)

    assert str(exc_info.value) == f"invalid message id 2 for {Challenge.TEXT}, expected {Challenge.TYPE}"


def test_parse_with_invalid_authmethod_type():
    message = [4, ["authmethod"], {}]
    with pytest.raises(ValueError) as exc_info:
        Challenge.parse(message)

    assert str(exc_info.value) == f"{Challenge.TEXT}: value at index 1 must be of type '{util.STRING}' but was list"


def test_parse_with_invalid_extra_type():
    message = [4, "anonymous", "extra"]
    with pytest.raises(ValueError) as exc_info:
        Challenge.parse(message)

    assert str(exc_info.value) == f"{Challenge.TEXT}: value at index 2 must be of type '{util.DICT}' but was str"


def test_parse_correctly():
    authmethod = "cryptosign"
    extra = {"channel_binding": "tls-unique"}
    message = [4, authmethod, extra]
    challenge = Challenge.parse(message)

    assert isinstance(challenge, Challenge)

    assert isinstance(challenge.authmethod, str)
    assert challenge.authmethod == authmethod

    assert isinstance(challenge.extra, dict)
    assert challenge.extra == extra


def test_marshal_without_extra():
    authmethod = "cryptosign"
    message = Challenge(authmethod).marshal()

    assert isinstance(message, list)

    assert isinstance(message[0], int)
    assert message[0] == Challenge.TYPE

    assert isinstance(message[1], str)
    assert message[1] == authmethod

    assert message[2] == dict()


def test_marshal_with_extra():
    authmethod = "wamp-scram"
    extra = {"iterations": 4096}
    message = Challenge(authmethod, extra).marshal()

    assert isinstance(message, list)

    assert isinstance(message[0], int)
    assert message[0] == Challenge.TYPE

    assert isinstance(message[1], str)
    assert message[1] == authmethod

    assert isinstance(message[2], dict)
    assert message[2] == extra
