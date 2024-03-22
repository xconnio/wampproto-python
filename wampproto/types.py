class SessionDetails:
    def __init__(self, session_id: int, realm: str, authid: str, authrole: str):
        self._session_id = session_id
        self._realm = realm
        self._authid = authid
        self._authrole = authrole

    @property
    def session_id(self) -> int:
        return self._session_id

    @property
    def realm(self) -> str:
        return self._realm

    @property
    def authid(self) -> str:
        return self._authid

    @property
    def authrole(self) -> str:
        return self._authrole
