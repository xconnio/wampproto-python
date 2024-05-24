from __future__ import annotations

from typing import Any

from wampproto.messages.message import Message
from wampproto.messages import util
from wampproto.messages.validation_spec import ValidationSpec


class Register(Message):
    TEXT = "REGISTER"
    TYPE = 64

    VALIDATION_SPEC = ValidationSpec(
        min_length=4,
        max_length=4,
        message=TEXT,
        spec={
            1: util.validate_request_id,
            2: util.validate_options,
            3: util.validate_uri,
        },
    )

    def __init__(self, request_id: int, uri: str, options: dict = None):
        super().__init__()
        self.request_id = request_id
        self.uri = uri
        self.options = options

    @classmethod
    def parse(cls, msg: list[Any]) -> Register:
        f = util.validate_message(msg, cls.TYPE, cls.TEXT, cls.VALIDATION_SPEC)
        return Register(f.request_id, f.uri, f.options)

    def marshal(self) -> list[Any]:
        return [self.TYPE, self.request_id, self.options, self.uri]
