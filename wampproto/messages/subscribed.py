from __future__ import annotations

from typing import Any

from wampproto.messages.message import Message
from wampproto.messages import util
from wampproto.messages.validation_spec import ValidationSpec


class Subscribed(Message):
    TEXT = "SUBSCRIBED"
    TYPE = 33

    VALIDATION_SPEC = ValidationSpec(
        min_length=3,
        max_length=3,
        message=TEXT,
        spec={
            1: util.validate_request_id,
            2: util.validate_subscription_id,
        },
    )

    def __init__(self, request_id: int, subscription_id: int):
        super().__init__()
        self.request_id = request_id
        self.subscription_id = subscription_id

    @classmethod
    def parse(cls, msg: list[Any]) -> Subscribed:
        f = util.validate_message(msg, cls.TYPE, cls.TEXT, cls.VALIDATION_SPEC)
        return Subscribed(f.request_id, f.subscription_id)

    def marshal(self) -> list[Any]:
        return [self.TYPE, self.request_id, self.subscription_id]
