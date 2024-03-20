from wamp import messages

CLIENT_ROLES = {
    "caller": {"features": {}},
    "callee": {"features": {}},
    "publisher": {"features": {}},
    "subscriber": {"features": {}},
}


class IClientAuthenticator:
    def details(self) -> dict:
        raise NotImplementedError()

    def authenticate(self, challenge: messages.Challenge) -> messages.Authenticate:
        raise NotImplementedError()
