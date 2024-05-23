import pytest

from wampproto.messages import util
from wampproto.messages import exceptions
from wampproto.messages.welcome import Welcome

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
    assert message[0] == Welcome.TYPE
    assert message[1] == session_id
    assert message[2] == expected_details


def test_marshal_with_no_roles_and_details():
    roles = {}
    details = {}
    message = Welcome(TEST_SESSION_ID, roles, **details).marshal()

    assert isinstance(message, list)
    assert len(message) == 3

    assert isinstance(message[0], int)
    assert message[0] == Welcome.TYPE

    assert isinstance(message[1], int)
    assert message[1] == TEST_SESSION_ID

    assert isinstance(message[2], dict)
    assert message[2] == {"roles": {}}


def test_marshal_with_role_and_no_details():
    roles = {"callee": {}}
    details = {}
    message = Welcome(TEST_SESSION_ID, roles, **details).marshal()

    assert isinstance(message, list)
    assert len(message) == 3

    assert isinstance(message[0], int)
    assert message[0] == Welcome.TYPE

    assert isinstance(message[1], int)
    assert message[1] == TEST_SESSION_ID

    assert isinstance(message[2], dict)
    assert message[2] == {"roles": roles}


def test_marshal_with_authid():
    roles = {"callee": {}}
    details = {"authid": "mahad"}
    message = Welcome(TEST_SESSION_ID, roles, **details).marshal()

    assert isinstance(message, list)
    assert len(message) == 3

    assert isinstance(message[0], int)
    assert message[0] == Welcome.TYPE

    assert isinstance(message[1], int)
    assert message[1] == TEST_SESSION_ID

    assert isinstance(message[2], dict)
    assert message[2] == {"roles": roles, "authid": "mahad"}


def test_marshal_with_authrole():
    roles = {"callee": {}}
    details = {"authrole": "admin"}
    message = Welcome(TEST_SESSION_ID, roles, **details).marshal()

    assert isinstance(message, list)
    assert len(message) == 3

    assert isinstance(message[0], int)
    assert message[0] == Welcome.TYPE

    assert isinstance(message[1], int)
    assert message[1] == TEST_SESSION_ID

    assert isinstance(message[2], dict)
    assert message[2] == {"roles": roles, "authrole": "admin"}


def test_marshal_with_authmethod():
    roles = {"callee": {}}
    details = {"authmethod": "anonymous"}
    message = Welcome(TEST_SESSION_ID, roles, **details).marshal()

    assert isinstance(message, list)
    assert len(message) == 3

    assert isinstance(message[0], int)
    assert message[0] == Welcome.TYPE

    assert isinstance(message[1], int)
    assert message[1] == TEST_SESSION_ID

    assert isinstance(message[2], dict)
    assert message[2] == {"roles": roles, "authmethod": "anonymous"}


def test_marshal_with_authextra():
    roles = {"callee": {}}
    details = {"authextra": {"extra": True}}
    message = Welcome(TEST_SESSION_ID, roles, **details).marshal()

    assert isinstance(message, list)
    assert len(message) == 3

    assert isinstance(message[0], int)
    assert message[0] == Welcome.TYPE

    assert isinstance(message[1], int)
    assert message[1] == TEST_SESSION_ID

    assert isinstance(message[2], dict)
    assert message[2] == {"roles": roles, "authextra": {"extra": True}}


def test_marshal_with_role_authid_and_authrole():
    roles = {"callee": {}}
    details = {"authid": "mahad", "authrole": "admin"}
    message = Welcome(TEST_SESSION_ID, roles, **details).marshal()

    assert isinstance(message, list)
    assert len(message) == 3

    assert isinstance(message[0], int)
    assert message[0] == Welcome.TYPE

    assert isinstance(message[1], int)
    assert message[1] == TEST_SESSION_ID

    assert isinstance(message[2], dict)
    assert message[2] == {"roles": roles, "authid": "mahad", "authrole": "admin"}


def test_marshal_with_role_authid_authrole_authmethod():
    roles = {"callee": {}}
    details = {"authid": "mahad", "authrole": "admin", "authmethod": "ticket"}
    message = Welcome(TEST_SESSION_ID, roles, **details).marshal()

    assert isinstance(message, list)
    assert len(message) == 3

    assert isinstance(message[0], int)
    assert message[0] == Welcome.TYPE

    assert isinstance(message[1], int)
    assert message[1] == TEST_SESSION_ID

    assert isinstance(message[2], dict)
    assert message[2] == {"roles": roles, "authid": "mahad", "authrole": "admin", "authmethod": "ticket"}


def test_marshal_with_role_authid_authrole_authmethod_authextra():
    roles = {"callee": {}}
    details = {"authid": "mahad", "authrole": "admin", "authmethod": "ticket", "authextra": {"authprovider": "static"}}
    message = Welcome(TEST_SESSION_ID, roles, **details).marshal()

    assert isinstance(message, list)
    assert len(message) == 3

    assert isinstance(message[0], int)
    assert message[0] == Welcome.TYPE

    assert isinstance(message[1], int)
    assert message[1] == TEST_SESSION_ID

    assert isinstance(message[2], dict)
    assert message[2] == {
        "roles": roles,
        "authid": "mahad",
        "authrole": "admin",
        "authmethod": "ticket",
        "authextra": {"authprovider": "static"},
    }


def test_parse_with_invalid_type():
    message = "msg"
    with pytest.raises(ValueError) as exc_info:
        Welcome.parse(message)

    assert (
        str(exc_info.value)
        == f"invalid message type {type(message).__name__} for {Welcome.TEXT}, type should be a list"
    )


def test_parse_with_invalid_list_min_length():
    message = [2]
    with pytest.raises(ValueError) as exc_info:
        Welcome.parse(message)

    assert str(exc_info.value) == f"invalid message length {len(message)}, must be at least 3"


def test_parse_with_invalid_list_max_length():
    message = [1, 5, 23, 1]
    with pytest.raises(ValueError) as exc_info:
        Welcome.parse(message)

    assert str(exc_info.value) == f"invalid message length {len(message)}, must be at most 3"


def test_parse_with_invalid_message_type():
    message = [1, TEST_SESSION_ID, {}]
    with pytest.raises(ValueError) as exc_info:
        Welcome.parse(message)

    assert str(exc_info.value) == f"invalid message id 1 for {Welcome.TEXT}, expected {Welcome.TYPE}"


def test_parse_with_invalid_session_type():
    message = [2, ["session"], {"roles": {"callee": {}}}]
    with pytest.raises(ValueError) as exc_info:
        Welcome.parse(message)

    assert str(exc_info.value) == f"{Welcome.TEXT}: value at index 1 must be of type 'int' but was list"


def test_parse_with_negative_session_value():
    message = [2, -1, {"roles": {"callee": {}}}]
    with pytest.raises(ValueError) as exc_info:
        Welcome.parse(message)

    assert (
        str(exc_info.value)
        == f"{Welcome.TEXT}: value at index 1 must be between '{util.MIN_ID}' and '{util.MAX_ID}' but was -1"
    )


def test_parse_with_out_of_range_session_value():
    value = 9007199254740993
    message = [2, value, {"roles": {"callee": {}}}]
    with pytest.raises(ValueError) as exc_info:
        Welcome.parse(message)

    assert (
        str(exc_info.value)
        == f"{Welcome.TEXT}: value at index 1 must be between '{util.MIN_ID}' and '{util.MAX_ID}' but was {value}"
    )


def test_parse_with_invalid_details_type():
    message = [2, TEST_SESSION_ID, "details"]
    with pytest.raises(ValueError) as exc_info:
        Welcome.parse(message)

    assert str(exc_info.value) == f"{Welcome.TEXT}: value at index 2 must be of type 'dict' but was str"


def test_parse_with_invalid_details_dict_key():
    message = [2, TEST_SESSION_ID, {1: "v"}]
    with pytest.raises(ValueError) as exc_info:
        Welcome.parse(message)

    assert (
        str(exc_info.value)
        == f"{Welcome.TEXT}: value at index 2 for key 'roles' must be of type 'dict' but was NoneType"
    )


def test_parse_with_invalid_role_type():
    message = [2, TEST_SESSION_ID, {"roles": "new_role"}]
    with pytest.raises(ValueError) as exc_info:
        Welcome.parse(message)

    assert str(exc_info.value) == f"{Welcome.TEXT}: value at index 2 for key 'roles' must be of type 'dict' but was str"


def test_parse_with_empty_role():
    message = [2, TEST_SESSION_ID, {"roles": {}}]
    with pytest.raises(ValueError) as exc_info:
        Welcome.parse(message)

    assert (
        str(exc_info.value)
        == f"{Welcome.TEXT}: value at index 2 for roles key must be in {util.AllowedRoles.get_allowed_roles()} but was empty"
    )


def test_parse_with_invalid_role_key():
    message = [2, TEST_SESSION_ID, {"roles": {"new_role": {}}}]
    with pytest.raises(ValueError) as exc_info:
        Welcome.parse(message)

    assert (
        str(exc_info.value)
        == f"{Welcome.TEXT}: value at index 2 for roles key must be in {util.AllowedRoles.get_allowed_roles()} but was new_role"
    )


def test_parse_with_invalid_authid():
    message = [2, TEST_SESSION_ID, {"roles": {"callee": {}}, "authid": []}]
    with pytest.raises(ValueError) as exc_info:
        Welcome.parse(message)

    assert (
        str(exc_info.value)
        == f"{Welcome.TEXT}: value at index 2 for key 'authid' must be of type 'string' but was list"
    )


def test_parse_with_invalid_authrole():
    message = [2, TEST_SESSION_ID, {"roles": {"callee": {}}, "authrole": []}]
    with pytest.raises(ValueError) as exc_info:
        Welcome.parse(message)

    assert (
        str(exc_info.value)
        == f"{Welcome.TEXT}: value at index 2 for key 'authrole' must be of type 'string' but was list"
    )


def test_parse_with_invalid_authmethod_type():
    message = [2, TEST_SESSION_ID, {"roles": {"callee": {}}, "authmethod": []}]
    with pytest.raises(ValueError) as exc_info:
        Welcome.parse(message)

    assert (
        str(exc_info.value)
        == f"{Welcome.TEXT}: value at index 2 for key 'authmethod' must be of type 'string' but was list"
    )


def test_parse_with_invalid_authextra_type():
    message = [2, TEST_SESSION_ID, {"roles": {"callee": {}}, "authextra": "authextra"}]
    with pytest.raises(ValueError) as exc_info:
        Welcome.parse(message)

    assert (
        str(exc_info.value)
        == f"{Welcome.TEXT}: value at index 2 for key 'authextra' must be of type 'dict' but was str"
    )


def test_parse_with_valid_roles():
    for role in util.AllowedRoles.get_allowed_roles():
        details = {"roles": {role: {}}}
        welcome = Welcome.parse([Welcome.TYPE, TEST_SESSION_ID, details])

        assert isinstance(welcome, Welcome)
        assert isinstance(welcome.session_id, int)
        assert welcome.session_id == TEST_SESSION_ID

        assert isinstance(welcome.roles, dict)
        assert welcome.roles == details["roles"]

        assert welcome.authid is None
        assert welcome.authrole is None
        assert welcome.authmethod is None
        assert welcome.authextra is None


def test_parse_with_multiple_roles():
    details = {"roles": {"callee": {}, "caller": {}}}
    welcome = Welcome.parse([Welcome.TYPE, TEST_SESSION_ID, details])

    assert isinstance(welcome, Welcome)
    assert isinstance(welcome.session_id, int)
    assert welcome.session_id == TEST_SESSION_ID

    assert isinstance(welcome.roles, dict)
    assert welcome.roles == details["roles"]

    assert welcome.authid is None
    assert welcome.authrole is None
    assert welcome.authmethod is None
    assert welcome.authextra is None


def test_parse_with_authid():
    details = {"roles": {"callee": {}}, "authid": "mahad"}
    welcome = Welcome.parse([Welcome.TYPE, TEST_SESSION_ID, details])

    assert isinstance(welcome, Welcome)
    assert isinstance(welcome.session_id, int)
    assert welcome.session_id == TEST_SESSION_ID

    assert isinstance(welcome.roles, dict)
    assert welcome.roles == details["roles"]

    assert isinstance(welcome.authid, str)
    assert welcome.authid == details["authid"]
    assert welcome.authrole is None
    assert welcome.authmethod is None
    assert welcome.authextra is None


def test_parse_with_authrole():
    details = {"roles": {"callee": {}}, "authrole": "admin"}
    welcome = Welcome.parse([Welcome.TYPE, TEST_SESSION_ID, details])

    assert isinstance(welcome, Welcome)
    assert isinstance(welcome.session_id, int)
    assert welcome.session_id == TEST_SESSION_ID

    assert isinstance(welcome.roles, dict)
    assert welcome.roles == details["roles"]

    assert isinstance(welcome.authrole, str)
    assert welcome.authrole == details["authrole"]
    assert welcome.authid is None
    assert welcome.authmethod is None
    assert welcome.authextra is None


def test_parse_with_authmethod():
    details = {"roles": {"callee": {}}, "authmethod": "cryptosign"}
    welcome = Welcome.parse([Welcome.TYPE, TEST_SESSION_ID, details])

    assert isinstance(welcome, Welcome)
    assert isinstance(welcome.session_id, int)
    assert welcome.session_id == TEST_SESSION_ID

    assert isinstance(welcome.roles, dict)
    assert welcome.roles == details["roles"]

    assert isinstance(welcome.authmethod, str)
    assert welcome.authmethod == details["authmethod"]
    assert welcome.authid is None
    assert welcome.authrole is None
    assert welcome.authextra is None


def test_parse_with_authid_and_authrole():
    details = {"roles": {"callee": {}}, "authid": "mahad", "authrole": "admin"}
    welcome = Welcome.parse([Welcome.TYPE, TEST_SESSION_ID, details])

    assert isinstance(welcome, Welcome)
    assert isinstance(welcome.session_id, int)
    assert welcome.session_id == TEST_SESSION_ID

    assert isinstance(welcome.roles, dict)
    assert welcome.roles == details["roles"]

    assert isinstance(welcome.authid, str)
    assert welcome.authid == details["authid"]

    assert isinstance(welcome.authrole, str)
    assert welcome.authrole == details["authrole"]
    assert welcome.authmethod is None
    assert welcome.authextra is None


def test_parse_with_authid_authrole_authmethod():
    details = {"roles": {"callee": {}}, "authid": "mahad", "authrole": "admin", "authmethod": "cryptosign"}
    welcome = Welcome.parse([Welcome.TYPE, TEST_SESSION_ID, details])

    assert isinstance(welcome, Welcome)
    assert isinstance(welcome.session_id, int)
    assert welcome.session_id == TEST_SESSION_ID

    assert isinstance(welcome.roles, dict)
    assert welcome.roles == details["roles"]

    assert isinstance(welcome.authid, str)
    assert welcome.authid == details["authid"]

    assert isinstance(welcome.authrole, str)
    assert welcome.authrole == details["authrole"]

    assert isinstance(welcome.authmethod, str)
    assert welcome.authmethod == details["authmethod"]
    assert welcome.authextra is None


def test_parse_with_authid_authrole_authmethod_authextra():
    details = {
        "roles": {"callee": {}},
        "authid": "mahad",
        "authrole": "admin",
        "authmethod": "cryptosign",
        "authextra": {"extra": True},
    }
    welcome = Welcome.parse([Welcome.TYPE, TEST_SESSION_ID, details])

    assert isinstance(welcome, Welcome)
    assert isinstance(welcome.session_id, int)
    assert welcome.session_id == TEST_SESSION_ID

    assert isinstance(welcome.roles, dict)
    assert welcome.roles == details["roles"]

    assert isinstance(welcome.authid, str)
    assert welcome.authid == details["authid"]

    assert isinstance(welcome.authrole, str)
    assert welcome.authrole == details["authrole"]

    assert isinstance(welcome.authmethod, str)
    assert welcome.authmethod == details["authmethod"]

    assert isinstance(welcome.authextra, dict)
    assert len(welcome.authextra) == 1
    assert welcome.authextra == details["authextra"]
