from typing import Any

import pytest

from wamp.messages import error
from wamp.messages.welcome import Welcome

TEST_SESSION_ID = 25631


@pytest.mark.parametrize(
    "session_id, roles, details, expected_details",
    [
        (TEST_SESSION_ID, {}, {}, {"roles": {}}),
        (TEST_SESSION_ID, {"caller": ""}, {"authid": "mahad"}, {"roles": {"caller": ""}, "authid": "mahad"}),
        (TEST_SESSION_ID, {"caller": ""}, {"authrole": "callee"}, {"roles": {"caller": ""}, "authrole": "callee"}),
        (
            TEST_SESSION_ID,
            {"publisher": ""},
            {"authrole": "callee", "authid": "mahad"},
            {"roles": {"publisher": ""}, "authrole": "callee", "authid": "mahad"},
        ),
    ],
)
def test_welcome(session_id, roles, details, expected_details):
    message = Welcome(session_id, roles, **details).marshal()

    assert isinstance(message, list)
    assert len(message) == 3
    assert message[0] == Welcome.MESSAGE_TYPE
    assert message[1] == session_id
    assert message[2] == expected_details


@pytest.mark.parametrize(
    "message, error_msg, error_type",
    [
        (
            "tes",
            f"invalid message type '<class 'str'>' for {Welcome.WELCOME_TEXT}, type should be a list",
            error.ProtocolError,
        ),
        (
            [1],
            f"invalid message length '1' for {Welcome.WELCOME_TEXT}, length should be equal to three",
            error.ProtocolError,
        ),
        ([1, TEST_SESSION_ID, {}], f"invalid message type for {Welcome.WELCOME_TEXT}", error.ProtocolError),
        (
            [Welcome.MESSAGE_TYPE, None, {}],
            f"session ID must be an integer for {Welcome.WELCOME_TEXT}",
            error.ProtocolError,
        ),
        (
            [Welcome.MESSAGE_TYPE, "session", {}],
            f"session ID must be an integer for {Welcome.WELCOME_TEXT}",
            error.ProtocolError,
        ),
        ([2, -1, {}], f"invalid Session ID value for {Welcome.WELCOME_TEXT}", error.ProtocolError),
        ([2, 9007199254740993, {}], f"invalid Session ID value for {Welcome.WELCOME_TEXT}", error.ProtocolError),
        (
            [2, TEST_SESSION_ID, "details"],
            f"details must be of type dictionary for {Welcome.WELCOME_TEXT}",
            error.InvalidDetailsError,
        ),
        (
            [2, TEST_SESSION_ID, {1: "v"}],
            f"invalid type for key '1' in extra details for {Welcome.WELCOME_TEXT}",
            error.InvalidDetailsError,
        ),
        (
            [2, TEST_SESSION_ID, {"k": "v", 2: "v"}],
            f"invalid type for key '2' in extra details for {Welcome.WELCOME_TEXT}",
            error.InvalidDetailsError,
        ),
        (
            [2, TEST_SESSION_ID, {"roles": "new_role"}],
            f"invalid type for 'roles' in details for {Welcome.WELCOME_TEXT}",
            error.ProtocolError,
        ),
        (
            [2, TEST_SESSION_ID, {"roles": {}}],
            f"roles are missing in details for {Welcome.WELCOME_TEXT}",
            error.ProtocolError,
        ),
        (
            [2, TEST_SESSION_ID, {"roles": {"new_role": {}}}],
            f"invalid role 'new_role' in 'roles' details for {Welcome.WELCOME_TEXT}",
            error.ProtocolError,
        ),
        (
            [2, TEST_SESSION_ID, {"roles": {"callee": {}}, "authid": []}],
            f"authid must be a type string for {Welcome.WELCOME_TEXT}",
            error.ProtocolError,
        ),
        (
            [2, TEST_SESSION_ID, {"roles": {"callee": {}}, "authrole": []}],
            f"authrole must be a type string for {Welcome.WELCOME_TEXT}",
            error.ProtocolError,
        ),
    ],
)
def test_welcome_parse_incorrectly(message, error_msg, error_type):
    with pytest.raises(error_type) as exc_info:
        Welcome.parse(message)

    assert str(exc_info.value) == error_msg


@pytest.mark.parametrize(
    "msg_type, session_id, details",
    [
        ([2, TEST_SESSION_ID, {"roles": {"callee": {}}}]),
        ([Welcome.MESSAGE_TYPE, TEST_SESSION_ID, {"roles": {"callee": {}}}]),
        ([Welcome.MESSAGE_TYPE, TEST_SESSION_ID, {"roles": {"caller": {}}}]),
        ([Welcome.MESSAGE_TYPE, TEST_SESSION_ID, {"roles": {"publisher": {}}}]),
        ([Welcome.MESSAGE_TYPE, TEST_SESSION_ID, {"roles": {"subscriber": {}}}]),
        ([Welcome.MESSAGE_TYPE, TEST_SESSION_ID, {"roles": {"callee": {}}, "authid": "mahad"}]),
        ([Welcome.MESSAGE_TYPE, TEST_SESSION_ID, {"roles": {"callee": {}}, "authrole": "admin"}]),
        ([Welcome.MESSAGE_TYPE, TEST_SESSION_ID, {"roles": {"callee": {}}, "authid": "mahad", "authrole": "admin"}]),
        ([Welcome.MESSAGE_TYPE, TEST_SESSION_ID, {"roles": {"callee": {}}, "authid": "mahad", "authrole": "admin"}]),
        (
            [
                Welcome.MESSAGE_TYPE,
                TEST_SESSION_ID,
                {"roles": {"subscriber": {}, "publisher": {}, "callee": {}, "caller": {}}},
            ]
        ),
    ],
)
def test_welcome_parse(msg_type: int, session_id: str, details: dict[str, Any]):
    welcome = Welcome.parse([msg_type, session_id, details])

    assert welcome.session_id == session_id
    assert welcome.roles == details["roles"]
    assert welcome.authid == details.get("authid", None)
    assert welcome.authrole == details.get("authrole", None)
