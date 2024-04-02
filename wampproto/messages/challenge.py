from __future__ import annotations

from typing import Any

from wampproto.messages import util, exceptions
from wampproto.messages.message import Message


class Challenge(Message):
    TEXT = "CHALLENGE"
    TYPE = 4

    def __init__(self, authmethod: str, extra: dict | None = None):
        super().__init__()
        self.authmethod = authmethod
        self.extra = {} if extra is None else extra

    @staticmethod
    def parse(msg: list[Any]) -> Challenge:
        util.sanity_check(msg, 3, 3, Challenge.TYPE, Challenge.TEXT)

        authmethod = msg[1]
        if not isinstance(authmethod, str):
            raise exceptions.ProtocolError(f"invalid type {type(authmethod)} for 'authmethod' in {Challenge.TEXT}")

        extra = util.validate_details_or_raise(msg[2], Challenge.TEXT)

        return Challenge(authmethod, extra)

    def marshal(self) -> list[Any]:
        return [Challenge.TYPE, self.authmethod, self.extra]
