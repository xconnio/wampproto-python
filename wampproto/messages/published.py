from __future__ import annotations

from typing import Any

from wampproto.messages.message import Message
from wampproto.messages import util
from wampproto.messages.validation_spec import ValidationSpec


class Published(Message):
    TEXT = "PUBLISHED"
    TYPE = 17

    VALIDATION_SPEC = ValidationSpec(
        min_length=3,
        max_length=3,
        message=TEXT,
        spec={
            1: util.validate_request_id,
            2: util.validate_publication_id,
        },
    )

    def __init__(self, request_id: int, publication_id: int):
        super().__init__()
        self.request_id = request_id
        self.publication_id = publication_id

    @classmethod
    def parse(cls, msg: list[Any]) -> Published:
        f = util.validate_message(msg, cls.TYPE, cls.TEXT, cls.VALIDATION_SPEC)
        return Published(f.request_id, f.publication_id)

    def marshal(self) -> list[Any]:
        return [self.TYPE, self.request_id, self.publication_id]
