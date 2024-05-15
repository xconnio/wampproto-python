from __future__ import annotations

from typing import Any

from wampproto.messages.message import Message
from wampproto.messages import util


class Registered(Message):
    TEXT = "REGISTERED"
    TYPE = 65

    def __init__(self, request_id: int, registration_id: int):
        super().__init__()
        self.request_id = request_id
        self.registration_id = registration_id

    @classmethod
    def parse(cls, msg: list[Any]) -> Registered:
        util.sanity_check(msg, 3, 3, cls.TYPE, cls.TEXT)

        request_id = util.validate_session_id_or_raise(msg[1], cls.TEXT, "request ID")
        registration_id = util.validate_session_id_or_raise(msg[2], cls.TEXT, "registration ID")

        return Registered(request_id, registration_id)

    def marshal(self) -> list[Any]:
        return [self.TYPE, self.request_id, self.registration_id]
