import pytest

from wampproto.messages import util
from wampproto.messages import exceptions
from wampproto.messages.hello import Hello


def test_marshal_with_no_roles_and_details():
    realm = "realm"
    roles = {}
    details = {}
    message = Hello(realm, roles, **details).marshal()

    assert isinstance(message, list)
    assert len(message) == 3

    assert isinstance(message[0], int)
    assert message[0] == Hello.TYPE

    assert isinstance(message[1], str)
    assert message[1] == realm

    assert isinstance(message[2], dict)
    assert message[2] == {"roles": {}}


def test_marshal_with_role_and_no_details():
    realm = "realm"
    roles = {"callee": {}}
    details = {}
    message = Hello(realm, roles, **details).marshal()

    assert isinstance(message, list)
    assert len(message) == 3

    assert isinstance(message[0], int)
    assert message[0] == Hello.TYPE

    assert isinstance(message[1], str)
    assert message[1] == realm

    assert isinstance(message[2], dict)
    assert message[2] == {"roles": roles}


def test_marshal_with_authid():
    realm = "realm"
    roles = {"callee": {}}
    details = {"authid": "mahad"}
    message = Hello(realm, roles, **details).marshal()

    assert isinstance(message, list)
    assert len(message) == 3

    assert isinstance(message[0], int)
    assert message[0] == Hello.TYPE

    assert isinstance(message[1], str)
    assert message[1] == realm

    assert isinstance(message[2], dict)
    assert message[2] == {"roles": roles, "authid": "mahad"}


def test_marshal_with_authrole():
    realm = "realm"
    roles = {"callee": {}}
    details = {"authrole": "admin"}
    message = Hello(realm, roles, **details).marshal()

    assert isinstance(message, list)
    assert len(message) == 3

    assert isinstance(message[0], int)
    assert message[0] == Hello.TYPE

    assert isinstance(message[1], str)
    assert message[1] == realm

    assert isinstance(message[2], dict)
    assert message[2] == {"roles": roles, "authrole": "admin"}


def test_marshal_with_authmethods():
    realm = "realm"
    roles = {"callee": {}}
    details = {"authmethods": ["ticket"]}
    message = Hello(realm, roles, **details).marshal()

    assert isinstance(message, list)
    assert len(message) == 3

    assert isinstance(message[0], int)
    assert message[0] == Hello.TYPE

    assert isinstance(message[1], str)
    assert message[1] == realm

    assert isinstance(message[2], dict)
    assert message[2] == {"roles": roles, "authmethods": ["ticket"]}


def test_marshal_with_authextra():
    realm = "realm"
    roles = {"callee": {}}
    details = {"authextra": {"authproivder": "static"}}
    message = Hello(realm, roles, **details).marshal()

    assert isinstance(message, list)
    assert len(message) == 3

    assert isinstance(message[0], int)
    assert message[0] == Hello.TYPE

    assert isinstance(message[1], str)
    assert message[1] == realm

    assert isinstance(message[2], dict)
    assert message[2] == {"roles": roles, "authextra": {"authproivder": "static"}}


def test_marshal_with_role_authid_and_authrole():
    realm = "realm"
    roles = {"callee": {}}
    details = {"authid": "mahad", "authrole": "admin"}
    message = Hello(realm, roles, **details).marshal()

    assert isinstance(message, list)
    assert len(message) == 3

    assert isinstance(message[0], int)
    assert message[0] == Hello.TYPE

    assert isinstance(message[1], str)
    assert message[1] == realm

    assert isinstance(message[2], dict)
    assert message[2] == {"roles": roles, "authid": "mahad", "authrole": "admin"}


def test_marshal_with_role_authid_authrole_authmethods():
    realm = "realm"
    roles = {"callee": {}}
    details = {"authid": "mahad", "authrole": "admin", "authmethods": ["ticket"]}
    message = Hello(realm, roles, **details).marshal()

    assert isinstance(message, list)
    assert len(message) == 3

    assert isinstance(message[0], int)
    assert message[0] == Hello.TYPE

    assert isinstance(message[1], str)
    assert message[1] == realm

    assert isinstance(message[2], dict)
    assert message[2] == {"roles": roles, "authid": "mahad", "authrole": "admin", "authmethods": ["ticket"]}


def test_marshal_with_role_authid_authrole_authmethods_authextra():
    realm = "realm"
    roles = {"callee": {}}
    details = {"authid": "mahad", "authrole": "admin", "authmethods": ["ticket"], "authextra": {"extra": True}}
    message = Hello(realm, roles, **details).marshal()

    assert isinstance(message, list)
    assert len(message) == 3

    assert isinstance(message[0], int)
    assert message[0] == Hello.TYPE

    assert isinstance(message[1], str)
    assert message[1] == realm

    assert isinstance(message[2], dict)
    assert message[2] == {
        "roles": roles,
        "authid": "mahad",
        "authrole": "admin",
        "authmethods": ["ticket"],
        "authextra": {"extra": True},
    }


def test_parse_with_invalid_type():
    message = "msg"
    with pytest.raises(ValueError) as exc_info:
        Hello.parse(message)

    assert (
        str(exc_info.value) == f"invalid message type {type(message).__name__} for {Hello.TEXT}, type should be a list"
    )


def test_parse_with_invalid_list_min_length():
    message = [1]
    with pytest.raises(ValueError) as exc_info:
        Hello.parse(message)

    assert str(exc_info.value) == f"invalid message length {len(message)}, must be at least 3"


def test_parse_with_invalid_list_max_length():
    message = [1, 5, 23, 1]
    with pytest.raises(ValueError) as exc_info:
        Hello.parse(message)

    assert str(exc_info.value) == f"invalid message length {len(message)}, must be at most 3"


def test_parse_with_invalid_message_type():
    message = [2, "realm", {}]
    with pytest.raises(ValueError) as exc_info:
        Hello.parse(message)

    assert str(exc_info.value) == f"invalid message id 2 for {Hello.TEXT}, expected 1"


def test_parse_with_realm_none():
    message = [1, None, {}]
    with pytest.raises(exceptions.InvalidRealmError) as exc_info:
        Hello.parse(message)

    assert str(exc_info.value) == f"realm cannot be null for {Hello.TEXT}"


def test_parse_with_invalid_realm_type():
    message = [1, {"realm": "realm1"}, {}]
    with pytest.raises(exceptions.InvalidRealmError) as exc_info:
        Hello.parse(message)

    assert str(exc_info.value) == f"realm must be of type string for {Hello.TEXT}"


def test_parse_with_invalid_details_type():
    message = [1, "realm1", "details"]
    with pytest.raises(exceptions.InvalidDetailsError) as exc_info:
        Hello.parse(message)

    assert str(exc_info.value) == f"details must be of type dictionary for {Hello.TEXT}"


def test_parse_with_invalid_details_dict_key():
    message = [1, "realm1", {1: "v"}]
    with pytest.raises(exceptions.InvalidDetailsError) as exc_info:
        Hello.parse(message)

    assert str(exc_info.value) == f"invalid type for key '1' in extra details for {Hello.TEXT}"


def test_parse_with_invalid_role_type():
    message = [1, "realm1", {"roles": "new_role"}]
    with pytest.raises(exceptions.ProtocolError) as exc_info:
        Hello.parse(message)

    assert str(exc_info.value) == f"invalid type for 'roles' in details for {Hello.TEXT}"


def test_parse_with_empty_role():
    message = [1, "realm1", {"roles": {}}]
    with pytest.raises(exceptions.ProtocolError) as exc_info:
        Hello.parse(message)

    assert str(exc_info.value) == f"roles are missing in details for {Hello.TEXT}"


def test_parse_with_invalid_role_key():
    message = [1, "realm1", {"roles": {"new_role": {}}}]
    with pytest.raises(exceptions.ProtocolError) as exc_info:
        Hello.parse(message)

    assert str(exc_info.value) == f"invalid role 'new_role' in 'roles' details for {Hello.TEXT}"


def test_parse_with_invalid_authid():
    message = [1, "realm1", {"roles": {"callee": {}}, "authid": []}]
    with pytest.raises(exceptions.ProtocolError) as exc_info:
        Hello.parse(message)

    assert str(exc_info.value) == f"authid must be a type string for {Hello.TEXT}"


def test_parse_with_invalid_authrole():
    message = [1, "realm1", {"roles": {"callee": {}}, "authrole": []}]
    with pytest.raises(exceptions.ProtocolError) as exc_info:
        Hello.parse(message)

    assert str(exc_info.value) == f"authrole must be a type string for {Hello.TEXT}"


def test_parse_with_invalid_authmethods_type():
    message = [1, "realm1", {"roles": {"callee": {}}, "authmethods": "authmethods"}]
    with pytest.raises(exceptions.InvalidTypeError) as exc_info:
        Hello.parse(message)

    assert str(exc_info.value) == f"invalid type: expected type 'list', got 'str' for authmethods in '{Hello.TEXT}'"


def test_parse_with_invalid_authmethods_item_type():
    message = [1, "realm1", {"roles": {"callee": {}}, "authmethods": ["ticket", 23]}]
    with pytest.raises(exceptions.InvalidTypeError) as exc_info:
        Hello.parse(message)

    assert (
        str(exc_info.value)
        == f"invalid type: expected type 'str', got 'int' for item '23' in 'authmethods' in '{Hello.TEXT}'"
    )


def test_parse_with_invalid_authextra_type():
    message = [1, "realm1", {"roles": {"callee": {}}, "authextra": "authextra"}]
    with pytest.raises(exceptions.InvalidTypeError) as exc_info:
        Hello.parse(message)

    assert str(exc_info.value) == f"invalid type: expected type 'dict', got 'str' for authextra in '{Hello.TEXT}'"


def test_parse_with_valid_roles():
    realm = "realm1"
    for role in util.AllowedRoles.get_allowed_roles():
        details = {"roles": {role: {}}}
        hello = Hello.parse([Hello.TYPE, realm, details])

        assert isinstance(hello, Hello)
        assert isinstance(hello.realm, str)
        assert hello.realm == realm

        assert isinstance(hello.roles, dict)
        assert hello.roles == details["roles"]

        assert hello.authid is None
        assert hello.authrole is None
        assert hello.authmethods is None
        assert hello.authextra is None


def test_parse_with_multiple_roles():
    realm = "realm1"
    details = {"roles": {"callee": {}, "caller": {}}}
    hello = Hello.parse([Hello.TYPE, realm, details])

    assert isinstance(hello, Hello)
    assert isinstance(hello.realm, str)
    assert hello.realm == realm

    assert isinstance(hello.roles, dict)
    assert hello.roles == details["roles"]

    assert hello.authid is None
    assert hello.authrole is None
    assert hello.authmethods is None
    assert hello.authextra is None


def test_parse_with_authid():
    realm = "realm1"
    details = {"roles": {"callee": {}}, "authid": "mahad"}
    hello = Hello.parse([Hello.TYPE, realm, details])

    assert isinstance(hello, Hello)
    assert isinstance(hello.realm, str)
    assert hello.realm == realm

    assert isinstance(hello.roles, dict)
    assert hello.roles == details["roles"]

    assert isinstance(hello.authid, str)
    assert hello.authid == details["authid"]
    assert hello.authrole is None
    assert hello.authmethods is None
    assert hello.authextra is None


def test_parse_with_authrole():
    realm = "realm1"
    details = {"roles": {"callee": {}}, "authrole": "admin"}
    hello = Hello.parse([Hello.TYPE, realm, details])

    assert isinstance(hello, Hello)
    assert isinstance(hello.realm, str)
    assert hello.realm == realm

    assert isinstance(hello.roles, dict)
    assert hello.roles == details["roles"]

    assert isinstance(hello.authrole, str)
    assert hello.authrole == details["authrole"]
    assert hello.authid is None
    assert hello.authmethods is None
    assert hello.authextra is None


def test_parse_with_authmethods():
    realm = "realm1"
    details = {"roles": {"callee": {}}, "authmethods": ["wampcra"]}
    hello = Hello.parse([Hello.TYPE, realm, details])

    assert isinstance(hello, Hello)
    assert isinstance(hello.realm, str)
    assert hello.realm == realm

    assert isinstance(hello.roles, dict)
    assert hello.roles == details["roles"]

    assert isinstance(hello.authmethods, list)
    assert len(hello.authmethods) == 1
    assert hello.authmethods[0] == "wampcra"

    assert hello.authrole is None
    assert hello.authid is None
    assert hello.authextra is None


def test_parse_with_authextra():
    realm = "realm1"
    details = {"roles": {"callee": {}}, "authextra": {"extra": True}}
    hello = Hello.parse([Hello.TYPE, realm, details])

    assert isinstance(hello, Hello)
    assert isinstance(hello.realm, str)
    assert hello.realm == realm

    assert isinstance(hello.roles, dict)
    assert hello.roles == details["roles"]

    assert isinstance(hello.authextra, dict)
    assert len(hello.authextra) == 1
    assert hello.authextra == {"extra": True}

    assert hello.authrole is None
    assert hello.authid is None
    assert hello.authmethods is None


def test_parse_with_authid_authrole_authmethods():
    realm = "realm1"
    details = {"roles": {"callee": {}}, "authid": "mahad", "authrole": "admin", "authmethods": ["wampcra"]}
    hello = Hello.parse([Hello.TYPE, realm, details])

    assert isinstance(hello, Hello)
    assert isinstance(hello.realm, str)
    assert hello.realm == realm

    assert isinstance(hello.roles, dict)
    assert hello.roles == details["roles"]

    assert isinstance(hello.authid, str)
    assert hello.authid == details["authid"]

    assert isinstance(hello.authrole, str)
    assert hello.authrole == details["authrole"]

    assert isinstance(hello.authmethods, list)
    assert len(hello.authmethods) == 1
    assert hello.authmethods[0] == "wampcra"

    assert hello.authextra is None


def test_parse_with_authid_authrole_authmethods_authextra():
    realm = "realm1"
    details = {
        "roles": {"callee": {}},
        "authid": "mahad",
        "authrole": "admin",
        "authmethods": ["wampcra"],
        "authextra": {"provider": "dynamic"},
    }
    hello = Hello.parse([Hello.TYPE, realm, details])

    assert isinstance(hello, Hello)
    assert isinstance(hello.realm, str)
    assert hello.realm == realm

    assert isinstance(hello.roles, dict)
    assert hello.roles == details["roles"]

    assert isinstance(hello.authid, str)
    assert hello.authid == details["authid"]

    assert isinstance(hello.authrole, str)
    assert hello.authrole == details["authrole"]

    assert isinstance(hello.authmethods, list)
    assert len(hello.authmethods) == 1
    assert hello.authmethods[0] == "wampcra"

    assert isinstance(hello.authextra, dict)
    assert len(hello.authextra) == 1
    assert hello.authextra == {"provider": "dynamic"}
