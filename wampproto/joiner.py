from typing import Optional

from wampproto import messages, serializers, auth
from wampproto.types import SessionDetails
from wampproto.messages.hello import HelloFields
from wampproto.exception import ApplicationError

CLIENT_ROLES = {
    "caller": {"features": {}},
    "callee": {"features": {}},
    "publisher": {"features": {}},
    "subscriber": {"features": {}},
}


class Joiner:
    STATE_NONE = 0
    STATE_HELLO_SENT = 1
    STATE_AUTHENTICATE_SENT = 2
    STATE_JOINED = 3

    def __init__(
        self,
        realm: str,
        serializer: serializers.Serializer = serializers.JSONSerializer(),
        authenticator: auth.IClientAuthenticator = None,
    ):
        self._realm = realm
        self._serializer = serializer
        self._authenticator = authenticator if authenticator is not None else auth.AnonymousAuthenticator("", {})
        self._state = Joiner.STATE_NONE

        self._session_details: SessionDetails = None

    def send_hello(self, roles: dict[str, dict[str, dict[str, bool]]] = None) -> bytes:
        if roles is None:
            roles = CLIENT_ROLES

        hello = messages.Hello(
            HelloFields(
                realm=self._realm,
                roles=roles,
                authid=self._authenticator.authid,
                authmethods=[self._authenticator.auth_method],
                authextra=self._authenticator.auth_extra,
            )
        )

        self._state = Joiner.STATE_HELLO_SENT
        return self._serializer.serialize(hello)

    def receive(self, data: bytes) -> Optional[bytes]:
        received_message = self._serializer.deserialize(data)

        to_send = self.receive_message(received_message)
        if to_send is not None and isinstance(to_send, messages.Authenticate):
            return self._serializer.serialize(to_send)

    def receive_message(self, msg: messages.Message) -> Optional[messages.Message]:
        if isinstance(msg, messages.Welcome):
            if self._state != Joiner.STATE_HELLO_SENT and self._state != Joiner.STATE_AUTHENTICATE_SENT:
                raise ValueError("received welcome when it was not expected")

            self._session_details = SessionDetails(msg.session_id, self._realm, msg.authid, msg.authrole)
            self._state = Joiner.STATE_JOINED
        elif isinstance(msg, messages.Challenge):
            if self._state != Joiner.STATE_HELLO_SENT:
                raise ValueError("received welcome when it was not expected")

            authenticate = self._authenticator.authenticate(msg)
            self._state = Joiner.STATE_AUTHENTICATE_SENT
            return authenticate
        elif isinstance(msg, messages.Abort):
            raise ApplicationError(msg.reason, msg.args, msg.kwargs)
        else:
            raise ValueError("received unknown message")

    def get_session_details(self) -> SessionDetails:
        if self._session_details is None:
            raise ValueError("session is not setup yet")

        return self._session_details
