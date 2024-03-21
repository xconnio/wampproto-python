from wampproto import messages
from wampproto.auth.auth import IClientAuthenticator


class TicketAuthenticator(IClientAuthenticator):
    TYPE = "ticket"

    def __init__(self, authid: str, auth_extra: dict, ticket: str):
        super().__init__(TicketAuthenticator.TYPE, authid, auth_extra)
        self._ticket = ticket

    def authenticate(self, challenge: messages.Challenge) -> messages.Authenticate:
        return messages.Authenticate(self._ticket, {})
