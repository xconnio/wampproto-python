from __future__ import annotations

from typing import Any

from wamp.messages import error, util
from wamp.messages.message import Message


class Authenticate(Message):
    AUTHENTICATE_TEXT = "AUTHENTICATE"
    MESSAGE_TYPE = 5

    def __init__(self, signature: str, extra: dict | None = None):
        super().__init__()
        self.signature = signature
        self.extra = {} if extra is None else extra

    @staticmethod
    def parse(msg: list[Any]) -> Authenticate:
        util.sanity_check(msg, 3, 3, Authenticate.MESSAGE_TYPE, Authenticate.AUTHENTICATE_TEXT)

        signature = msg[1]
        if not isinstance(signature, str):
            raise error.ProtocolError(
                f"invalid type {type(signature)} for 'signature' in {Authenticate.AUTHENTICATE_TEXT}"
            )

        extra = util.validate_details_or_raise(msg[2], Authenticate.AUTHENTICATE_TEXT)

        return Authenticate(signature, extra)

    def marshal(self) -> list[Any]:
        return [Authenticate.MESSAGE_TYPE, self.signature, self.extra]
