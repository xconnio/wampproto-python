from wampproto import messages, auth


class AnonymousAuthenticator(auth.IClientAuthenticator):
    TYPE = "anonymous"

    def __init__(self, authid: str, auth_extra: dict | None = None):
        super().__init__(AnonymousAuthenticator.TYPE, authid, auth_extra)

    def authenticate(self, challenge: messages.Challenge) -> messages.Authenticate:
        raise NotImplementedError()
