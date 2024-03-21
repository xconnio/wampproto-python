from __future__ import annotations

from typing import Any

from wampproto.wamp.messages import error, util
from wampproto.wamp.messages.message import Message


class Challenge(Message):
    CHALLENGE_TEXT = "CHALLENGE"
    MESSAGE_TYPE = 4

    def __init__(self, authmethod: str, extra: dict | None = None):
        super().__init__()
        self.authmethod = authmethod
        self.extra = {} if extra is None else extra

    @staticmethod
    def parse(msg: list[Any]) -> Challenge:
        util.sanity_check(msg, 3, 3, Challenge.MESSAGE_TYPE, Challenge.CHALLENGE_TEXT)

        authmethod = msg[1]
        if not isinstance(authmethod, str):
            raise error.ProtocolError(f"invalid type {type(authmethod)} for 'authmethod' in {Challenge.CHALLENGE_TEXT}")

        extra = util.validate_details_or_raise(msg[2], Challenge.CHALLENGE_TEXT)

        return Challenge(authmethod, extra)

    def marshal(self) -> list[Any]:
        return [Challenge.MESSAGE_TYPE, self.authmethod, self.extra]
