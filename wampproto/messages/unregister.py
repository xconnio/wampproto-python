from typing import Any

from wampproto.messages.message import Message
from wampproto.messages import util


class UnRegister(Message):
    TEXT = "UNREGISTER"
    TYPE = 66

    def __init__(self, request_id: int, registration_id: int):
        super().__init__()
        self.request_id = request_id
        self.registration_id = registration_id

    @staticmethod
    def parse(msg: list[Any]) -> "UnRegister":
        util.sanity_check(msg, 3, 3, UnRegister.TYPE, UnRegister.TEXT)

        request_id = util.validate_session_id_or_raise(msg[1], UnRegister.TEXT, "request ID")
        registration_id = util.validate_session_id_or_raise(msg[2], UnRegister.TEXT, "registration ID")

        return UnRegister(request_id, registration_id)

    def marshal(self) -> list[Any]:
        return [UnRegister.TYPE, self.request_id, self.registration_id]
