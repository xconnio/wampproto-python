from typing import Any

from wampproto.messages.message import Message
from wampproto.messages import util


class Registered(Message):
    Registered_Text = "REGISTERED"
    MESSAGE_TYPE = 65

    def __init__(self, request_id: int, registration_id: int):
        super().__init__()
        self.request_id = request_id
        self.registration_id = registration_id

    @staticmethod
    def parse(msg: list[Any]) -> "Registered":
        util.sanity_check(msg, 3, 3, Registered.MESSAGE_TYPE, Registered.Registered_Text)

        request_id = util.validate_session_id_or_raise(msg[1], Registered.Registered_Text, "request ID")
        registration_id = util.validate_session_id_or_raise(msg[2], Registered.Registered_Text, "registration ID")

        return Registered(request_id, registration_id)

    def marshal(self) -> list[Any]:
        return [Registered.MESSAGE_TYPE, self.request_id, self.registration_id]
