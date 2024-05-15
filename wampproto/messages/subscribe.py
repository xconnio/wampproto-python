from __future__ import annotations

from typing import Any

from wampproto.messages.message import Message
from wampproto.messages import util


class Subscribe(Message):
    TEXT = "SUBSCRIBE"
    TYPE = 32

    def __init__(self, request_id: int, topic: str, options: dict = None):
        super().__init__()
        self.request_id = request_id
        self.topic: str = topic
        self.options = options if options else {}

    @classmethod
    def parse(cls, msg: list[Any]) -> Subscribe:
        util.sanity_check(msg, 4, 4, cls.TYPE, cls.TEXT)

        request_id = util.validate_session_id_or_raise(msg[1], cls.TEXT, "request ID")
        options = util.validate_details_or_raise(msg[2], cls.TEXT, "options")
        topic = util.validate_uri_or_raise(msg[3], "topic")

        return Subscribe(request_id, topic, options)

    def marshal(self) -> list[Any]:
        return [self.TYPE, self.request_id, self.options, self.topic]
