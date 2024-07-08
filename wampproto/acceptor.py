import binascii

from wampproto import messages, auth, serializers, uris
from wampproto.idgen import generate_session_id
from wampproto.types import SessionDetails

ROUTER_ROLES = {
    "dealer": {"features": {}},
    "broker": {"features": {}},
}


class Acceptor:
    STATE_NONE = 0
    STATE_HELLO_RECEIVED = 1
    STATE_CHALLENGE_SENT = 2
    STATE_WELCOME_SENT = 3
    STATE_ABORTED = 4

    TICKET = "ticket"
    WAMPCRA = "wampcra"
    ANONYMOUS = "anonymous"
    CRYPTOSIGN = "cryptosign"

    def __init__(
        self,
        serializer: serializers.Serializer = serializers.JSONSerializer(),
        authenticator: auth.IServerAuthenticator = None,
        roles: dict[str, dict[str, dict[str, bool]]] = None,
    ):
        self._serializer = serializer
        self._authenticator = authenticator
        self._roles = roles if roles is not None else ROUTER_ROLES

        self._state = Acceptor.STATE_NONE
        self._session_id = generate_session_id()

        self._auth_method: str = None
        self._hello: messages.Hello = None
        self._response: auth.Response = None
        self._session_details: SessionDetails = None

        self._public_key: str = None
        self._challenge: str = None
        self._secret: str = None

    def receive(self, data: bytes) -> (bytes, bool):
        received_message = self._serializer.deserialize(data)
        to_send = self.receive_message(received_message)

        return self._serializer.serialize(to_send), isinstance(to_send, messages.Welcome) or isinstance(
            to_send, messages.Abort
        )

    def receive_message(self, msg: messages.Message) -> messages.Message:
        if self._state == Acceptor.STATE_WELCOME_SENT:
            raise ValueError("session was established, not expecting any new messages")

        if isinstance(msg, messages.Hello):
            if self._state != Acceptor.STATE_NONE:
                raise ValueError("unknown state")

            if self._authenticator is None:
                self._state = Acceptor.STATE_WELCOME_SENT
                welcome = messages.Welcome(
                    messages.WelcomeFields(self._session_id, self._roles, "anonymous", "anonymous", "anonymous")
                )
                self._session_details = SessionDetails(welcome.session_id, msg.realm, welcome.authid, welcome.authrole)

                return welcome

            if msg.authmethods is not None and len(msg.authmethods) > 0:
                method = msg.authmethods[0]
            else:
                method = Acceptor.ANONYMOUS

            self._auth_method = method
            self._hello = msg

            match method:
                case Acceptor.ANONYMOUS:
                    request = auth.AnonymousRequest(msg.realm, msg.authid, msg.authextra)
                    try:
                        response = self._authenticator.authenticate(request)
                    except Exception as e:
                        return messages.Abort(messages.AbortFields({}, uris.AUTHENTICATION_FAILED, args=list(e.args)))

                    self._state = Acceptor.STATE_WELCOME_SENT

                    welcome = messages.Welcome(
                        messages.WelcomeFields(
                            self._session_id, self._roles, response.authid, response.authrole, method
                        )
                    )
                    self._session_details = SessionDetails(
                        welcome.session_id, msg.realm, welcome.authid, welcome.authrole
                    )

                    return welcome
                case Acceptor.CRYPTOSIGN:
                    public_key = msg.authextra.get("pubkey")
                    if public_key is None:
                        raise ValueError("authextra must contain pubkey for cryptosign")

                    request = auth.CryptoSignRequest(msg.realm, msg.authid, msg.authextra, public_key)
                    try:
                        self._response = self._authenticator.authenticate(request)
                    except Exception as e:
                        return messages.Abort(messages.AbortFields({}, uris.AUTHENTICATION_FAILED, args=list(e.args)))

                    self._public_key = public_key

                    challenge = auth.generate_cryptosign_challenge()
                    self._state = Acceptor.STATE_CHALLENGE_SENT

                    return messages.Challenge(messages.ChallengeFields(method, {"challenge": challenge}))
                case Acceptor.WAMPCRA:
                    request = auth.WAMPCRARequest(msg.realm, msg.authid, msg.authextra)
                    try:
                        response = self._authenticator.authenticate(request)
                    except Exception as e:
                        return messages.Abort(messages.AbortFields({}, uris.AUTHENTICATION_FAILED, args=list(e.args)))

                    if not isinstance(response, auth.WAMPCRAResponse):
                        raise ValueError("invalid response type for WAMPCRA")

                    self._response = response
                    self._secret = response.secret

                    challenge = auth.generate_wampcra_challenge(
                        self._session_id, self._response.authid, self._response.authrole, "dynamic"
                    )
                    self._state = Acceptor.STATE_CHALLENGE_SENT
                    self._challenge = challenge

                    return messages.Challenge(messages.ChallengeFields(method, {"challenge": challenge}))
                case Acceptor.TICKET:
                    self._state = Acceptor.STATE_CHALLENGE_SENT
                    return messages.Challenge(messages.ChallengeFields(method, {}))
                case _:
                    raise ValueError("unknown method")
        elif isinstance(msg, messages.Authenticate):
            if self._state != Acceptor.STATE_CHALLENGE_SENT:
                raise ValueError("unknown state")

            match self._auth_method:
                case Acceptor.CRYPTOSIGN:
                    if not auth.verify_cryptosign_signature(msg.signature, binascii.unhexlify(self._public_key)):
                        self._state = Acceptor.STATE_ABORTED
                        return messages.Abort(messages.AbortFields({}, uris.AUTHENTICATION_FAILED))

                    self._state = Acceptor.STATE_WELCOME_SENT
                    welcome = messages.Welcome(
                        messages.WelcomeFields(
                            self._session_id,
                            self._roles,
                            authid=self._response.authid,
                            authrole=self._response.authrole,
                        )
                    )
                    self._session_details = SessionDetails(
                        welcome.session_id, self._hello.realm, welcome.authid, welcome.authrole
                    )
                    return welcome
                case Acceptor.WAMPCRA:
                    if not auth.verify_wampcra_signature(msg.signature, self._challenge, self._secret.encode()):
                        self._state = Acceptor.STATE_ABORTED
                        return messages.Abort(messages.AbortFields({}, uris.AUTHENTICATION_FAILED))

                    self._state = Acceptor.STATE_WELCOME_SENT
                    welcome = messages.Welcome(
                        messages.WelcomeFields(
                            self._session_id,
                            self._roles,
                            authid=self._response.authid,
                            authrole=self._response.authrole,
                        )
                    )
                    self._session_details = SessionDetails(
                        welcome.session_id, self._hello.realm, welcome.authid, welcome.authrole
                    )
                    return welcome
                case Acceptor.TICKET:
                    request = auth.TicketRequest(
                        self._hello.realm, self._hello.authid, self._hello.authextra, msg.signature
                    )
                    try:
                        response = self._authenticator.authenticate(request)
                    except Exception as e:
                        return messages.Abort(messages.AbortFields({}, uris.AUTHENTICATION_FAILED, args=list(e.args)))

                    self._state = Acceptor.STATE_WELCOME_SENT
                    welcome = messages.Welcome(
                        messages.WelcomeFields(
                            self._session_id, self._roles, authid=response.authid, authrole=response.authrole
                        )
                    )
                    self._session_details = SessionDetails(
                        welcome.session_id, self._hello.realm, welcome.authid, welcome.authrole
                    )

                    return welcome
        elif isinstance(msg, messages.Abort):
            self._state = Acceptor.STATE_ABORTED

    def is_aborted(self) -> bool:
        return self._state == Acceptor.STATE_ABORTED

    def get_session_details(self) -> SessionDetails:
        if self._session_details is None:
            raise ValueError("session is not setup yet")

        return self._session_details
