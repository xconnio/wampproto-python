import pytest

from wamp.messages import error
from wamp.messages.authenticate import Authenticate


def test_parse_with_invalid_type():
    message = "msg"
    with pytest.raises(error.ProtocolError) as exc_info:
        Authenticate.parse(message)

    assert (
        str(exc_info.value)
        == f"invalid message type '{type(message)}' for {Authenticate.AUTHENTICATE_TEXT}, type should be a list"
    )


def test_parse_with_invalid_list_length():
    message = [5]
    with pytest.raises(error.ProtocolError) as exc_info:
        Authenticate.parse(message)

    assert (
        str(exc_info.value) == f"invalid message length '{len(message)}' for {Authenticate.AUTHENTICATE_TEXT}, "
        f"length should be equal to three"
    )


def test_parse_with_invalid_message_type():
    message = [4, "signature", {}]
    with pytest.raises(error.ProtocolError) as exc_info:
        Authenticate.parse(message)

    assert str(exc_info.value) == f"invalid message type for {Authenticate.AUTHENTICATE_TEXT}"


def test_parse_with_invalid_signature_type():
    message = [5, ["signature"], {}]
    with pytest.raises(error.ProtocolError) as exc_info:
        Authenticate.parse(message)

    assert str(exc_info.value) == f"invalid type {type(message[1])} for 'signature' in {Authenticate.AUTHENTICATE_TEXT}"


def test_parse_with_invalid_extra_type():
    message = [5, "signature", "extra"]
    with pytest.raises(error.InvalidDetailsError) as exc_info:
        Authenticate.parse(message)

    assert str(exc_info.value) == f"details must be of type dictionary for {Authenticate.AUTHENTICATE_TEXT}"


def test_parse_with_invalid_details_dict_key():
    message = [5, "signature", {1: "v"}]
    with pytest.raises(error.InvalidDetailsError) as exc_info:
        Authenticate.parse(message)

    assert str(exc_info.value) == f"invalid type for key '1' in extra details for {Authenticate.AUTHENTICATE_TEXT}"


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
    assert message[0] == Authenticate.MESSAGE_TYPE

    assert isinstance(message[1], str)
    assert message[1] == signature

    assert message[2] == dict()


def test_marshal_with_extra():
    signature = "signature"
    extra = {"channel_binding": "null"}
    message = Authenticate(signature, extra).marshal()

    assert isinstance(message, list)

    assert isinstance(message[0], int)
    assert message[0] == Authenticate.MESSAGE_TYPE

    assert isinstance(message[1], str)
    assert message[1] == signature

    assert isinstance(message[2], dict)
    assert message[2] == extra
