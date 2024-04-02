from __future__ import annotations

from typing import Any

from wampproto.messages import util
from wampproto.messages.message import Message


class Abort(Message):
    TEXT = "ABORT"
    TYPE = 3

    def __init__(self, details: dict, reason: str):
        super().__init__()
        self.details = details
        self.reason = reason

    @staticmethod
    def parse(msg: list[Any]) -> Abort:
        util.sanity_check(msg, 3, 3, Abort.TYPE, Abort.TEXT)

        details = util.validate_details_or_raise(msg[1], Abort.TEXT)

        reason = util.validate_uri_or_raise(msg[2], Abort.TEXT)

        return Abort(details, reason)

    def marshal(self) -> list[Any]:
        return [Abort.TYPE, self.details, self.reason]
