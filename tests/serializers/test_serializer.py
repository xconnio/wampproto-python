import pytest

from wampproto.serializers.serializer import to_message


def test_to_message_with_invalid_type():
    message = "Hello World!"
    with pytest.raises(TypeError) as exc_info:
        to_message(message)

    assert str(exc_info.value) == f"invalid type '{type(message)}', expected a list"


def test_to_message_with_invalid_message_type():
    message = ["hi"]
    with pytest.raises(TypeError) as exc_info:
        to_message(message)

    assert str(exc_info.value) == f"invalid message type '{type(message[0])}', expected an integer"


def test_to_message_with_invalid_case():
    with pytest.raises(ValueError) as exc_info:
        to_message([999])

    assert str(exc_info.value) == "unknown message type"


def test_to_message_with_hello():
    realm = "realm1"
    details = {"roles": {"callee": {}}}
    hello = to_message([1, realm, details])
    assert hello.realm == realm
    assert hello.roles == details["roles"]


def test_to_message_with_welcome():
    session_id = 231
    details = {"roles": {"callee": {}}}
    welcome = to_message([2, session_id, details])
    assert welcome.session_id == session_id
    assert welcome.roles == details["roles"]


def test_to_message_with_abort():
    details = {"message": "The realm does not exist."}
    reason = "wamp.error.no_such_realm"
    abort = to_message([3, details, reason])
    assert abort.details == details
    assert abort.reason == reason


def test_to_message_with_challenge():
    authmethod = "cryptosign"
    extra = {"channel_binding": "tls-unique"}
    challenge = to_message([4, authmethod, extra])
    assert challenge.authmethod == authmethod
    assert challenge.extra == extra


def test_to_message_with_authenticate():
    signature = "signature"
    extra = {"channel_binding": "null"}
    authenticate = to_message([5, signature, extra])
    assert authenticate.signature == signature
    assert authenticate.extra == extra


def test_to_message_with_goodbye():
    details = {"message": "The host is shutting down now."}
    reason = "wamp.close.system_shutdown"
    goodbye = to_message([6, details, reason])
    assert goodbye.details == details
    assert goodbye.reason == reason
