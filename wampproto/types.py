from dataclasses import dataclass

from wampproto import messages


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

    def __eq__(self, __value: "SessionDetails") -> bool:
        if __value is None or not isinstance(__value, SessionDetails):
            return False

        return (
            self.session_id == __value.session_id
            and self.realm == __value.realm
            and self.authid == __value.authid
            and self.authrole == __value.authrole
        )


@dataclass
class MessageWithRecipient:
    message: messages.Message
    recipient: int


@dataclass
class Publication:
    event: messages.Event | None = None
    recipients: list[int] = None
    ack: MessageWithRecipient | None = None
