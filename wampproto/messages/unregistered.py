from typing import Any

from wampproto.messages.message import Message
from wampproto.messages import util


class UnRegistered(Message):
    TEXT = "UNREGISTERED"
    TYPE = 67

    def __init__(self, request_id: int):
        super().__init__()
        self.request_id = request_id

    @staticmethod
    def parse(msg: list[Any]) -> "UnRegistered":
        util.sanity_check(msg, 2, 2, UnRegistered.TYPE, UnRegistered.TEXT)

        request_id = util.validate_session_id_or_raise(msg[1], UnRegistered.TEXT, "request ID")

        return UnRegistered(request_id)

    def marshal(self) -> list[Any]:
        return [UnRegistered.TYPE, self.request_id]
