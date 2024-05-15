from __future__ import annotations

from typing import Any

from wampproto.messages.message import Message
from wampproto.messages import util


class UnSubscribed(Message):
    TEXT = "UNSUBSCRIBED"
    TYPE = 35

    def __init__(self, request_id: int):
        super().__init__()
        self.request_id = request_id

    @classmethod
    def parse(cls, msg: list[Any]) -> UnSubscribed:
        util.sanity_check(msg, 2, 2, cls.TYPE, cls.TEXT)

        request_id = util.validate_session_id_or_raise(msg[1], cls.TEXT, "request ID")

        return UnSubscribed(request_id)

    def marshal(self) -> list[Any]:
        return [self.TYPE, self.request_id]
