from __future__ import annotations

from typing import Any

from wampproto.messages.message import Message
from wampproto.messages import util
from wampproto.messages.validation_spec import ValidationSpec


class IUnregisteredFields:
    @property
    def request_id(self):
        raise NotImplementedError


class UnregisteredFields(IUnregisteredFields):
    def __init__(self, request_id: int):
        super().__init__()
        self._request_id = request_id

    @property
    def request_id(self) -> int:
        return self._request_id


class Unregistered(Message):
    TEXT = "UNREGISTERED"
    TYPE = 67

    VALIDATION_SPEC = ValidationSpec(
        min_length=2,
        max_length=2,
        message=TEXT,
        spec={
            1: util.validate_request_id,
        },
    )

    def __init__(self, fields: IUnregisteredFields):
        super().__init__()
        self._fields = fields

    @property
    def request_id(self) -> int:
        return self._fields.request_id

    @classmethod
    def parse(cls, msg: list[Any]) -> Unregistered:
        f = util.validate_message(msg, cls.TYPE, cls.VALIDATION_SPEC)
        return Unregistered(UnregisteredFields(f.request_id))

    def marshal(self) -> list[Any]:
        return [self.TYPE, self.request_id]
