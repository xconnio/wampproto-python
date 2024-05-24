from __future__ import annotations

from typing import Any

from wampproto.messages.message import Message
from wampproto.messages import util
from wampproto.messages.validation_spec import ValidationSpec


class Subscribe(Message):
    TEXT = "SUBSCRIBE"
    TYPE = 32

    VALIDATION_SPEC = ValidationSpec(
        min_length=4,
        max_length=4,
        message=TEXT,
        spec={
            1: util.validate_request_id,
            2: util.validate_options,
            3: util.validate_topic,
        },
    )

    def __init__(self, request_id: int, topic: str, options: dict = None):
        super().__init__()
        self.request_id = request_id
        self.topic: str = topic
        self.options = options if options else {}

    @classmethod
    def parse(cls, msg: list[Any]) -> Subscribe:
        f = util.validate_message(msg, cls.TYPE, cls.TEXT, cls.VALIDATION_SPEC)
        return Subscribe(f.request_id, f.topic, f.options)

    def marshal(self) -> list[Any]:
        return [self.TYPE, self.request_id, self.options, self.topic]
