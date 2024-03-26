import pytest

from wampproto import joiner, acceptor, serializers, auth

PRIVATE_KEY = "49fe40797d16012c92004a19cdd217a2b74ac825e3855d445c455988d70c8973"


class Authenticator(auth.IServerAuthenticator):
    def methods(self) -> list[str]:
        return ["cryptosign", "ticket", "wampcra", "anonymous"]

    def authenticate(self, request: auth.Request) -> auth.Response:
        if request.method == "anonymous":
            return auth.Response(authid=request.authid, authrole="anonymous")
        elif request.method == "ticket":
            return auth.Response(request.authid, authrole="anonymous")
        elif request.method == "wampcra":
            return auth.WAMPCRAResponse(authid=request.authid, authrole="anonymous", secret="password")
        elif request.method == "cryptosign":
            return auth.Response(request.authid, authrole="anonymous")


@pytest.mark.parametrize(
    "serializer", [serializers.JSONSerializer(), serializers.CBORSerializer(), serializers.MsgPackSerializer()]
)
def test_join_no_auth(serializer):
    authenticator = auth.AnonymousAuthenticator("anonymous", {})
    j = joiner.Joiner("realm1", serializer, authenticator)
    hello = j.send_hello()
    assert hello is not None
    assert isinstance(hello, bytes)

    a = acceptor.Acceptor(serializer)
    data, final = a.receive(hello)
    assert data is not None and isinstance(data, bytes)
    assert final

    # for WAMP joiner, when the call to Joiner.receive() returns None
    # that means the session has been joined
    data = j.receive(data)
    assert data is None

    assert a.get_session_details() == j.get_session_details()


@pytest.mark.parametrize(
    "serializer, authenticator",
    [
        (serializers.JSONSerializer(), auth.TicketAuthenticator("anonymous", "ticket", {})),
        (serializers.MsgPackSerializer(), auth.WAMPCRAAuthenticator("anonymous", "password", {})),
        (serializers.CBORSerializer(), auth.CryptoSignAuthenticator("anonymous", PRIVATE_KEY, {})),
    ],
)
def test_join_auth(serializer, authenticator):
    j = joiner.Joiner("realm1", serializer, authenticator)
    hello = j.send_hello()
    assert hello is not None

    a = acceptor.Acceptor(serializer=serializer, authenticator=Authenticator())
    data, final = a.receive(hello)
    assert data is not None and isinstance(data, bytes)
    assert final is False

    data = j.receive(data)
    assert data is not None

    # for acceptor to know if the "welcome" as been sent
    # it may check if the "final" bool is true.
    data, final = a.receive(data)
    assert data is not None and isinstance(data, bytes)
    assert final

    data = j.receive(data)
    assert data is None

    assert a.get_session_details() == j.get_session_details()
