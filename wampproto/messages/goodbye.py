from __future__ import annotations

from typing import Any

from wampproto.messages import util
from wampproto.messages.message import Message
from wampproto.messages.validation_spec import ValidationSpec


class IGoodbyeFields:
    @property
    def details(self):
        raise NotImplementedError

    @property
    def reason(self):
        raise NotImplementedError


class GoodbyeFields(IGoodbyeFields):
    def __init__(self, details: dict[str, Any], reason: str):
        self._details = details
        self._reason = reason

    @property
    def details(self) -> dict[str, Any]:
        return self._details

    @property
    def reason(self) -> str:
        return self._reason


class Goodbye(Message):
    TEXT = "GOODBYE"
    TYPE = 6

    VALIDATION_SPEC = ValidationSpec(
        min_length=3,
        max_length=3,
        message=TEXT,
        spec={
            1: util.validate_details,
            2: util.validate_reason,
        },
    )

    def __init__(self, fields: IGoodbyeFields):
        super().__init__()
        self._fields = fields

    @property
    def details(self) -> dict[str, Any]:
        return self._fields.details

    @property
    def reason(self) -> str:
        return self._fields.reason

    @classmethod
    def parse(cls, msg: list[Any]) -> Goodbye:
        f = util.validate_message(msg, cls.TYPE, cls.VALIDATION_SPEC)
        return Goodbye(GoodbyeFields(f.details, f.reason))

    def marshal(self) -> list[Any]:
        return [self.TYPE, self.details, self.reason]
