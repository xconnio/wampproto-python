import pytest

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
