from wampproto import messages
from wampproto.auth.auth import IClientAuthenticator


class AnonymousAuthenticator(IClientAuthenticator):
    TYPE = "anonymous"

    def __init__(self, authid: str, auth_extra: dict):
        super().__init__(AnonymousAuthenticator.TYPE, authid, auth_extra)

    def authenticate(self, challenge: messages.Challenge) -> messages.Authenticate:
        raise NotImplementedError()
