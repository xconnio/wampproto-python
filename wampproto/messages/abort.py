from __future__ import annotations

from typing import Any

from wampproto.messages import util
from wampproto.messages.message import Message
from wampproto.messages.validation_spec import ValidationSpec


class Abort(Message):
    TEXT = "ABORT"
    TYPE = 3

    VALIDATION_SPEC = ValidationSpec(
        min_length=3,
        max_length=3,
        message=TEXT,
        spec={
            1: util.validate_details,
            2: util.validate_reason,
        },
    )

    def __init__(self, details: dict, reason: str):
        super().__init__()
        self.details = details
        self.reason = reason

    @classmethod
    def parse(cls, msg: list[Any]) -> Abort:
        f = util.validate_message(msg, cls.TYPE, cls.TEXT, cls.VALIDATION_SPEC)
        return Abort(f.details, f.reason)

    def marshal(self) -> list[Any]:
        return [self.TYPE, self.details, self.reason]
