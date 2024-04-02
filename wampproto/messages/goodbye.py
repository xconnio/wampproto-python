from __future__ import annotations

from typing import Any

from wampproto.messages import util
from wampproto.messages.message import Message


class Goodbye(Message):
    TEXT = "GOODBYE"
    TYPE = 6

    def __init__(self, details: dict, reason: str):
        super().__init__()
        self.details = details
        self.reason = reason

    @staticmethod
    def parse(msg: list[Any]) -> Goodbye:
        util.sanity_check(msg, 3, 3, Goodbye.TYPE, Goodbye.TEXT)

        details = util.validate_details_or_raise(msg[1], Goodbye.TEXT)

        reason = util.validate_uri_or_raise(msg[2], Goodbye.TEXT)

        return Goodbye(details, reason)

    def marshal(self) -> list[Any]:
        return [Goodbye.TYPE, self.details, self.reason]
