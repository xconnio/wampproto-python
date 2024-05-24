from __future__ import annotations

from typing import Any

from wampproto.messages import util
from wampproto.messages.message import Message
from wampproto.messages.validation_spec import ValidationSpec


class Authenticate(Message):
    TEXT = "AUTHENTICATE"
    TYPE = 5

    VALIDATION_SPEC = ValidationSpec(
        min_length=3,
        max_length=3,
        message=TEXT,
        spec={
            1: util.validate_signature,
            2: util.validate_extra,
        },
    )

    def __init__(self, signature: str, extra: dict | None = None):
        super().__init__()
        self.signature = signature
        self.extra = {} if extra is None else extra

    @classmethod
    def parse(cls, msg: list[Any]) -> Authenticate:
        f = util.validate_message(msg, cls.TYPE, cls.TEXT, cls.VALIDATION_SPEC)
        return Authenticate(f.signature, f.extra)

    def marshal(self) -> list[Any]:
        return [self.TYPE, self.signature, self.extra]
