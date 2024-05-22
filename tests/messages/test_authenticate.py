import pytest

from wampproto.messages import util
from wampproto.messages import Authenticate


def test_parse_with_invalid_type():
    message = "msg"
    with pytest.raises(ValueError) as exc_info:
        Authenticate.parse(message)

    assert (
        str(exc_info.value)
        == f"invalid message type {type(message).__name__} for {Authenticate.TEXT}, type should be a list"
    )


def test_parse_with_invalid_min_length():
    message = [5]
    with pytest.raises(ValueError) as exc_info:
        Authenticate.parse(message)

    assert str(exc_info.value) == f"invalid message length {len(message)}, must be at least 3"


def test_parse_with_invalid_max_length():
    message = [5, 6, 4, 3]
    with pytest.raises(ValueError) as exc_info:
        Authenticate.parse(message)

    assert str(exc_info.value) == f"invalid message length {len(message)}, must be at most 3"


def test_parse_with_invalid_message_type():
    message = [4, "signature", {}]
    with pytest.raises(ValueError) as exc_info:
        Authenticate.parse(message)

    assert str(exc_info.value) == f"invalid message id 4 for {Authenticate.TEXT}, expected 5"


def test_parse_with_invalid_signature_type():
    message = [5, ["signature"], {}]
    with pytest.raises(ValueError) as exc_info:
        Authenticate.parse(message)

    assert str(exc_info.value) == f"{Authenticate.TEXT}: value at index 1 must be of type '{util.STRING}' but was list"


def test_parse_with_invalid_extra_type():
    message = [5, "signature", "extra"]
    with pytest.raises(ValueError) as exc_info:
        Authenticate.parse(message)

    assert str(exc_info.value) == f"{Authenticate.TEXT}: value at index 2 must be of type '{util.DICT}' but was str"


def test_parse_correctly():
    signature = "signature"
    extra = {"channel_binding": "null"}
    message = [5, signature, extra]
    authenticate = Authenticate.parse(message)

    assert isinstance(authenticate, Authenticate)

    assert isinstance(authenticate.signature, str)
    assert authenticate.signature == signature

    assert isinstance(authenticate.extra, dict)
    assert authenticate.extra == extra


def test_marshal_without_extra():
    signature = "signature"
    message = Authenticate(signature).marshal()

    assert isinstance(message, list)

    assert isinstance(message[0], int)
    assert message[0] == Authenticate.TYPE

    assert isinstance(message[1], str)
    assert message[1] == signature

    assert message[2] == dict()


def test_marshal_with_extra():
    signature = "signature"
    extra = {"channel_binding": "null"}
    message = Authenticate(signature, extra).marshal()

    assert isinstance(message, list)

    assert isinstance(message[0], int)
    assert message[0] == Authenticate.TYPE

    assert isinstance(message[1], str)
    assert message[1] == signature

    assert isinstance(message[2], dict)
    assert message[2] == extra
