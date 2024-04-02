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

    @staticmethod
    def parse(msg: list[Any]) -> "Registered":
        util.sanity_check(msg, 3, 3, Registered.TYPE, Registered.TEXT)

        request_id = util.validate_session_id_or_raise(msg[1], Registered.TEXT, "request ID")
        registration_id = util.validate_session_id_or_raise(msg[2], Registered.TEXT, "registration ID")

        return Registered(request_id, registration_id)

    def marshal(self) -> list[Any]:
        return [Registered.TYPE, self.request_id, self.registration_id]
