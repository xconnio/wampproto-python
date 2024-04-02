from __future__ import annotations

from typing import Any

from wampproto.messages import util, exceptions
from wampproto.messages.message import Message


class Authenticate(Message):
    TEXT = "AUTHENTICATE"
    TYPE = 5

    def __init__(self, signature: str, extra: dict | None = None):
        super().__init__()
        self.signature = signature
        self.extra = {} if extra is None else extra

    @staticmethod
    def parse(msg: list[Any]) -> Authenticate:
        util.sanity_check(msg, 3, 3, Authenticate.TYPE, Authenticate.TEXT)

        signature = msg[1]
        if not isinstance(signature, str):
            raise exceptions.ProtocolError(f"invalid type {type(signature)} for 'signature' in {Authenticate.TEXT}")

        extra = util.validate_details_or_raise(msg[2], Authenticate.TEXT)

        return Authenticate(signature, extra)

    def marshal(self) -> list[Any]:
        return [Authenticate.TYPE, self.signature, self.extra]
