from __future__ import annotations

from typing import Any

from wampproto.messages import util, Message
from wampproto.messages.validation_spec import ValidationSpec


class IInterruptFields:
    @property
    def request_id(self):
        raise NotImplementedError

    @property
    def options(self):
        raise NotImplementedError


class InterruptFields(IInterruptFields):
    def __init__(self, request_id: int, options: dict[str, Any] | None = None):
        self._request_id = request_id
        self._options = {} if options is None else options

    @property
    def request_id(self) -> int:
        return self._request_id

    @property
    def options(self) -> dict[str, Any]:
        return self._options


class Interrupt(Message):
    TEXT = "INTERRUPT"
    TYPE = 69

    VALIDATION_SPEC = ValidationSpec(
        min_length=3,
        max_length=3,
        message=TEXT,
        spec={
            1: util.validate_request_id,
            2: util.validate_options,
        },
    )

    def __init__(self, fields: IInterruptFields):
        super().__init__()
        self._fields = fields

    @property
    def request_id(self) -> int:
        return self._fields.request_id

    @property
    def options(self) -> dict[str, Any]:
        return self._fields.options

    @classmethod
    def parse(cls, msg: list[Any]) -> Interrupt:
        f = util.validate_message(msg, cls.TYPE, cls.VALIDATION_SPEC)
        return Interrupt(InterruptFields(f.request_id, f.options))

    def marshal(self) -> list[Any]:
        return [self.TYPE, self.request_id, self.options]
