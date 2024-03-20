from wamp import messages
from wamp.auth.auth import IClientAuthenticator, CLIENT_ROLES


class TicketAuthenticator(IClientAuthenticator):
    TYPE = "ticket"

    def __init__(self, authid: str, auth_extra: dict, ticket: str):
        super().__init__()
        self._authid = authid
        self._auth_extra = auth_extra
        self._ticket = ticket

    def details(self) -> dict:
        return {
            "authmethods": [TicketAuthenticator.TYPE],
            "authid": self._authid,
            "authextra": self._auth_extra,
            "roles": CLIENT_ROLES,
        }

    def authenticate(self, challenge: messages.Challenge) -> messages.Authenticate:
        return messages.Authenticate(self._ticket, {})
