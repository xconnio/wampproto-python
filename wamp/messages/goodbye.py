from __future__ import annotations

from typing import Any

from wamp.messages import error, util
from wamp.messages.message import Message


class Goodbye(Message):
    GOODBYE_TEXT = "GOODBYE"
    MESSAGE_TYPE = 6

    def __init__(self, details: dict, reason: str):
        super().__init__()
        self.details = details
        self.reason = reason

    @staticmethod
    def parse(msg: list[Any]) -> Goodbye:
        util.sanity_check(msg, 3, 3, Goodbye.MESSAGE_TYPE, Goodbye.GOODBYE_TEXT)

        details = util.validate_details_or_raise(msg[1], Goodbye.GOODBYE_TEXT)

        reason = util.validate_uri_or_raise(msg[2], Goodbye.GOODBYE_TEXT)

        return Goodbye(details, reason)

    def marshal(self) -> list[Any]:
        return [Goodbye.MESSAGE_TYPE, self.details, self.reason]
