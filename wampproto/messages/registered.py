from __future__ import annotations

from typing import Any

from wampproto.messages.message import Message
from wampproto.messages import util
from wampproto.messages.validation_spec import ValidationSpec


class IRegisteredFields:
    @property
    def request_id(self):
        raise NotImplementedError

    @property
    def registration_id(self):
        raise NotImplementedError


class RegisteredFields(IRegisteredFields):
    def __init__(self, request_id: int, registration_id: int):
        super().__init__()
        self._request_id = request_id
        self._registration_id = registration_id

    @property
    def request_id(self) -> int:
        return self._request_id

    @property
    def registration_id(self) -> int:
        return self._registration_id


class Registered(Message):
    TEXT = "REGISTERED"
    TYPE = 65

    VALIDATION_SPEC = ValidationSpec(
        min_length=3,
        max_length=3,
        message=TEXT,
        spec={
            1: util.validate_request_id,
            2: util.validate_registration_id,
        },
    )

    def __init__(self, fields: IRegisteredFields):
        super().__init__()
        self._fields = fields

    @property
    def request_id(self) -> int:
        return self._fields.request_id

    @property
    def registration_id(self) -> int:
        return self._fields.registration_id

    @classmethod
    def parse(cls, msg: list[Any]) -> Registered:
        f = util.validate_message(msg, cls.TYPE, cls.VALIDATION_SPEC)
        return Registered(RegisteredFields(f.request_id, f.registration_id))

    def marshal(self) -> list[Any]:
        return [self.TYPE, self.request_id, self.registration_id]
