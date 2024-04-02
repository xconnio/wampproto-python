from typing import Any

from wampproto.messages.message import Message
from wampproto.messages import util


class UnSubscribe(Message):
    TEXT = "UNSUBSCRIBE"
    TYPE = 34

    def __init__(self, request_id: int, subscription_id: int):
        super().__init__()
        self.request_id = request_id
        self.subscription_id = subscription_id

    @staticmethod
    def parse(msg: list[Any]) -> "UnSubscribe":
        util.sanity_check(msg, 3, 3, UnSubscribe.TYPE, UnSubscribe.TEXT)

        request_id = util.validate_session_id_or_raise(msg[1], UnSubscribe.TEXT, "request ID")
        subscription_id = util.validate_session_id_or_raise(msg[2], UnSubscribe.TEXT, "subscription ID")

        return UnSubscribe(request_id, subscription_id)

    def marshal(self) -> list[Any]:
        return [UnSubscribe.TYPE, self.request_id, self.subscription_id]
