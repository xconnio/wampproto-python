import pytest
from wampproto.auth import AnonymousAuthenticator
from wampproto.messages import Challenge


def test_authenticator():
    authid = "authID"
    auth_extra = {"extra": "data"}

    authenticator = AnonymousAuthenticator(authid, auth_extra)

    assert authenticator.authid == authid
    assert authenticator.auth_extra == auth_extra
    assert authenticator.auth_method == AnonymousAuthenticator.TYPE

    challenge = Challenge(authenticator.auth_method, {"challenge": "test"})
    with pytest.raises(NotImplementedError):
        authenticator.authenticate(challenge)
