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

    @property
    def args(self):
        raise NotImplementedError()

    @property
    def kwargs(self):
        raise NotImplementedError()


class AbortFields(IAbortFields):
    def __init__(self, details: dict, reason: str, args: list[Any] | None = None, kwargs: dict[str, Any] | None = None):
        super().__init__()
        self._details = details
        self._reason = reason
        self._args = args
        self._kwargs = kwargs

    @property
    def details(self) -> dict[str, Any]:
        return self._details

    @property
    def reason(self) -> str:
        return self._reason

    @property
    def args(self) -> list[Any] | None:
        return self._args

    @property
    def kwargs(self) -> dict[str, Any] | None:
        return self._kwargs


class Abort(Message):
    TEXT = "ABORT"
    TYPE = 3

    VALIDATION_SPEC = ValidationSpec(
        min_length=3,
        max_length=5,
        message=TEXT,
        spec={
            1: util.validate_details,
            2: util.validate_reason,
            3: util.validate_args,
            4: util.validate_kwargs,
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

    @property
    def args(self) -> list[Any] | None:
        return self._fields.args

    @property
    def kwargs(self) -> dict[str, Any] | None:
        return self._fields.kwargs

    @classmethod
    def parse(cls, msg: list[Any]) -> Abort:
        f = util.validate_message(msg, cls.TYPE, cls.VALIDATION_SPEC)
        return Abort(AbortFields(f.details, f.reason, f.args, f.kwargs))

    def marshal(self) -> list[Any]:
        return [self.TYPE, self.details, self.reason]
