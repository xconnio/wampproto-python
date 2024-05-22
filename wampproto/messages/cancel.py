from __future__ import annotations

from typing import Any

from wampproto.messages import util, Message
from wampproto.messages.validation_spec import ValidationSpec


class Cancel(Message):
    TEXT = "CANCEL"
    TYPE = 49

    VALIDATION_SPEC = ValidationSpec(
        min_length=3,
        max_length=3,
        message=TEXT,
        spec={
            1: util.validate_request_id,
            2: util.validate_options,
        },
    )

    def __init__(
        self,
        call_request_id: int,
        options: dict | None = None,
    ):
        super().__init__()
        self.call_request_id = call_request_id
        self.options = options if options is not None else {}

    @classmethod
    def parse(cls, msg: list[Any]) -> Cancel:
        f = util.validate_message(msg, cls.TYPE, cls.TEXT, cls.VALIDATION_SPEC)
        return Cancel(f.request_id, f.options)

    def marshal(self) -> list[Any]:
        return [self.TYPE, self.call_request_id, self.options]
