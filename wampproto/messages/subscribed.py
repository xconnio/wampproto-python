from typing import Any

from wampproto.messages.message import Message
from wampproto.messages import util


class Subscribed(Message):
    TEXT = "SUBSCRIBED"
    TYPE = 33

    def __init__(self, request_id: int, subscription_id: int):
        super().__init__()
        self.request_id = request_id
        self.subscription_id = subscription_id

    @staticmethod
    def parse(msg: list[Any]) -> "Subscribed":
        util.sanity_check(msg, 3, 3, Subscribed.TYPE, Subscribed.TEXT)

        request_id = util.validate_session_id_or_raise(msg[1], Subscribed.TEXT, "request ID")
        subscription_id = util.validate_session_id_or_raise(msg[2], Subscribed.TEXT, "subscription ID")

        return Subscribed(request_id, subscription_id)

    def marshal(self) -> list[Any]:
        return [Subscribed.TYPE, self.request_id, self.subscription_id]
