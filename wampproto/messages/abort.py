from __future__ import annotations

from typing import Any

from wampproto.messages import util
from wampproto.messages.message import Message
from wampproto.messages.validation_spec import ValidationSpec


class IAbortFields:
    @property
    def details(self):
        raise NotImplementedError()

    @property
    def reason(self):
        raise NotImplementedError()


class AbortFields(IAbortFields):
    def __init__(self, details: dict, reason: str):
        super().__init__()
        self._details = details
        self._reason = reason

    @property
    def details(self) -> dict[str, Any]:
        return self._details

    @property
    def reason(self) -> str:
        return self._reason


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

    def __init__(self, fields: IAbortFields):
        super().__init__()
        self._fields = fields

    @property
    def details(self) -> dict[str, Any]:
        return self._fields.details

    @property
    def reason(self) -> str:
        return self._fields.reason

    @classmethod
    def parse(cls, msg: list[Any]) -> Abort:
        f = util.validate_message(msg, cls.TYPE, cls.TEXT, cls.VALIDATION_SPEC)
        return Abort(AbortFields(f.details, f.reason))

    def marshal(self) -> list[Any]:
        return [self.TYPE, self.details, self.reason]
