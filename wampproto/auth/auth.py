from wampproto import messages


class IClientAuthenticator:
    def __init__(self, method: str, authid: str, auth_extra: dict | None = None):
        super().__init__()
        self._method = method
        self._authid = authid
        self._auth_extra = auth_extra if auth_extra is not None else {}

    @property
    def auth_method(self) -> str:
        return self._method

    @property
    def authid(self) -> str:
        return self._authid

    @property
    def auth_extra(self) -> dict:
        return self._auth_extra

    def authenticate(self, challenge: messages.Challenge) -> messages.Authenticate:
        raise NotImplementedError()


class Request:
    def __init__(self, method: str, realm: str, authid: str, auth_extra: dict, authrole: str | None = None):
        self._method = method
        self._realm = realm
        self._authid = authid
        self._authrole = authrole
        self._auth_extra = auth_extra

    @property
    def method(self) -> str:
        return self._method

    @property
    def realm(self) -> str:
        return self._realm

    @property
    def authid(self) -> str:
        return self._authid

    @property
    def authrole(self) -> str:
        return self._authrole

    @property
    def auth_extra(self) -> dict:
        return self._auth_extra


class TicketRequest(Request):
    def __init__(self, realm: str, authid: str, auth_extra: dict, ticket: str, authrole: str | None = None):
        super().__init__(method="ticket", realm=realm, authid=authid, auth_extra=auth_extra, authrole=authrole)
        self._ticket = ticket

    @property
    def ticket(self) -> str:
        return self._ticket


class AnonymousRequest(Request):
    def __init__(self, realm: str, authid: str, auth_extra: dict, authrole: str | None = None):
        super().__init__(method="anonymous", realm=realm, authid=authid, auth_extra=auth_extra, authrole=authrole)


class WAMPCRARequest(Request):
    def __init__(self, realm: str, authid: str, auth_extra: dict, authrole: str | None = None):
        super().__init__(method="wampcra", realm=realm, authid=authid, auth_extra=auth_extra, authrole=authrole)


class CryptoSignRequest(Request):
    def __init__(self, realm: str, authid: str, auth_extra: dict, public_key: str, authrole: str | None = None):
        super().__init__(method="cryptosign", realm=realm, authid=authid, auth_extra=auth_extra, authrole=authrole)
        self._public_key = public_key

    @property
    def public_key(self) -> str:
        return self._public_key


class Response:
    def __init__(self, authid: str, authrole: str):
        self._authid = authid
        self._authrole = authrole

    @property
    def authid(self) -> str:
        return self._authid

    @property
    def authrole(self) -> str:
        return self._authrole


class WAMPCRAResponse(Response):
    def __init__(self, authid: str, authrole: str, secret: str):
        super().__init__(authid, authrole)
        self._secret = secret

    @property
    def secret(self) -> str:
        return self._secret


class WAMPCRASaltedResponse(WAMPCRAResponse):
    def __init__(self, authid: str, authrole: str, secret: str, salt: str, iterations: int, keylen: int):
        super().__init__(authid, authrole, secret)
        self._salt = salt
        self._iterations = iterations
        self._keylen = keylen

    @property
    def salt(self) -> str:
        return self.salt

    @property
    def iterations(self) -> int:
        return self._iterations

    @property
    def keylen(self) -> int:
        return self._keylen


class IServerAuthenticator:
    def methods(self) -> list[str]:
        raise NotImplementedError()

    def authenticate(self, request: Request) -> Response:
        raise NotImplementedError()
