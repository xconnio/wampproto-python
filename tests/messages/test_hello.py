from typing import Any

import pytest

from wamp.messages import error
from wamp.messages.hello import Hello


@pytest.mark.parametrize(
    "realm, roles, details, expected_details",
    [
        ("realm", {}, {}, {"roles": {}}),
        ("realm", {"callee": ""}, {"authid": "mahad"}, {"roles": {"callee": ""}, "authid": "mahad"}),
        ("realm", {"callee": ""}, {"authrole": "callee"}, {"roles": {"callee": ""}, "authrole": "callee"}),
        (
            "realm",
            {"publisher": ""},
            {"authrole": "callee", "authid": "mahad"},
            {"roles": {"publisher": ""}, "authrole": "callee", "authid": "mahad"},
        ),
    ],
)
def test_hello(realm, roles, details, expected_details):
    message = Hello(realm, roles, **details).marshal()

    assert isinstance(message, list)
    assert len(message) == 3
    assert message[0] == Hello.MESSAGE_TYPE
    assert message[1] == realm
    assert message[2] == expected_details


@pytest.mark.parametrize(
    "message, error_msg, error_type",
    [
        (
            "tes",
            f"invalid message type '<class 'str'>' for {Hello.HELLO_TEXT}, type should be a list",
            error.ProtocolError,
        ),
        (
            [1],
            f"invalid message length '1' for {Hello.HELLO_TEXT}, length should be equal to three",
            error.ProtocolError,
        ),
        ([2, "realm", {}], f"invalid message type for {Hello.HELLO_TEXT}", error.ProtocolError),
        ([1, None, {}], f"realm cannot be null for {Hello.HELLO_TEXT}", error.InvalidRealmError),
        ([1, {"realm": "realm1"}, {}], f"realm must be of type string for {Hello.HELLO_TEXT}", error.InvalidRealmError),
        (
            [1, "realm1", "details"],
            f"details must be of type dictionary for {Hello.HELLO_TEXT}",
            error.InvalidDetailsError,
        ),
        (
            [1, "realm1", {1: "v"}],
            f"invalid type for key '1' in extra details for {Hello.HELLO_TEXT}",
            error.InvalidDetailsError,
        ),
        (
            [1, "realm1", {"k": "v", 2: "v"}],
            f"invalid type for key '2' in extra details for {Hello.HELLO_TEXT}",
            error.InvalidDetailsError,
        ),
        (
            [1, "realm1", {"roles": "new_role"}],
            f"invalid type for 'roles' in details for {Hello.HELLO_TEXT}",
            error.ProtocolError,
        ),
        ([1, "realm1", {"roles": {}}], f"roles are missing in details for {Hello.HELLO_TEXT}", error.ProtocolError),
        (
            [1, "realm1", {"roles": {"new_role": {}}}],
            f"invalid role 'new_role' in 'roles' details for {Hello.HELLO_TEXT}",
            error.ProtocolError,
        ),
        (
            [1, "realm1", {"roles": {"callee": {}}, "authid": []}],
            f"authid must be a type string for {Hello.HELLO_TEXT}",
            error.ProtocolError,
        ),
        (
            [1, "realm1", {"roles": {"callee": {}}, "authrole": []}],
            f"authrole must be a type string for {Hello.HELLO_TEXT}",
            error.ProtocolError,
        ),
    ],
)
def test_hello_parse_incorrectly(message, error_msg, error_type):
    with pytest.raises(error_type) as exc_info:
        Hello.parse(message)

    assert str(exc_info.value) == error_msg


@pytest.mark.parametrize(
    "msg_type, realm, details",
    [
        ([1, "realm1", {"roles": {"callee": {}}}]),
        ([Hello.MESSAGE_TYPE, "realm1", {"roles": {"callee": {}}}]),
        ([Hello.MESSAGE_TYPE, "realm1", {"roles": {"caller": {}}}]),
        ([Hello.MESSAGE_TYPE, "realm1", {"roles": {"publisher": {}}}]),
        ([Hello.MESSAGE_TYPE, "realm1", {"roles": {"subscriber": {}}}]),
        ([Hello.MESSAGE_TYPE, "realm1", {"roles": {"callee": {}}, "authid": "mahad"}]),
        ([Hello.MESSAGE_TYPE, "realm1", {"roles": {"callee": {}}, "authrole": "admin"}]),
        ([Hello.MESSAGE_TYPE, "realm1", {"roles": {"callee": {}}, "authid": "mahad", "authrole": "admin"}]),
        ([Hello.MESSAGE_TYPE, "realm1", {"roles": {"callee": {}}, "authid": "mahad", "authrole": "admin"}]),
        ([Hello.MESSAGE_TYPE, "realm1", {"roles": {"subscriber": {}, "publisher": {}, "callee": {}, "caller": {}}}]),
    ],
)
def test_hello_parse(msg_type: int, realm: str, details: dict[str, Any]):
    hello = Hello.parse([msg_type, realm, details])

    assert hello.realm == realm
    assert hello.roles == details["roles"]
    assert hello.authid == details.get("authid", None)
    assert hello.authrole == details.get("authrole", None)
