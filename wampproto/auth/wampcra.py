from wampproto import messages
from wampproto.auth.auth import IClientAuthenticator


class WAMPCRAAuthenticator(IClientAuthenticator):
    TYPE = "wampcra"

    def __init__(self, authid: str, auth_extra: dict, secret: str):
        super().__init__(WAMPCRAAuthenticator.TYPE, authid, auth_extra)
        self._secret = secret

    def authenticate(self, challenge: messages.Challenge) -> messages.Authenticate:
        return messages.Authenticate(self._secret, {})
