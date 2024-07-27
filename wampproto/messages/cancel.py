from __future__ import annotations

from typing import Any

from wampproto.messages import util, Message
from wampproto.messages.validation_spec import ValidationSpec


class ICancelFields:
    @property
    def request_id(self):
        raise NotImplementedError()

    @property
    def options(self):
        raise NotImplementedError()


class CancelFields(ICancelFields):
    def __init__(self, request_id: int, options: dict[str, Any] | None = None):
        super().__init__()
        self._request_id = request_id
        self._options = {} if options is None else options

    @property
    def request_id(self) -> int:
        return self._request_id

    @property
    def options(self) -> dict[str, Any]:
        return self._options


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

    def __init__(self, fields: ICancelFields):
        super().__init__()
        self._fields = fields

    @property
    def request_id(self) -> int:
        return self._fields.request_id

    @property
    def options(self) -> dict[str, Any]:
        return self._fields.options

    @classmethod
    def parse(cls, msg: list[Any]) -> Cancel:
        f = util.validate_message(msg, cls.TYPE, cls.VALIDATION_SPEC)
        return Cancel(CancelFields(f.request_id, f.options))

    def marshal(self) -> list[Any]:
        return [self.TYPE, self.request_id, self.options]
