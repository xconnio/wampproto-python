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

    @classmethod
    def parse(cls, msg: list[Any]) -> Challenge:
        util.sanity_check(msg, 3, 3, cls.TYPE, cls.TEXT)

        authmethod = msg[1]
        if not isinstance(authmethod, str):
            raise exceptions.ProtocolError(f"invalid type {type(authmethod)} for 'authmethod' in {cls.TEXT}")

        extra = util.validate_details_or_raise(msg[2], cls.TEXT)

        return Challenge(authmethod, extra)

    def marshal(self) -> list[Any]:
        return [self.TYPE, self.authmethod, self.extra]
