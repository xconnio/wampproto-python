from __future__ import annotations

from typing import Any

from wampproto.messages.message import Message
from wampproto.messages import util
from wampproto.messages.validation_spec import ValidationSpec


class IRegisterFields:
    @property
    def request_id(self):
        raise NotImplementedError

    @property
    def procedure(self):
        raise NotImplementedError

    @property
    def options(self):
        raise NotImplementedError


class RegisterFields(IRegisterFields):
    def __init__(self, request_id: int, procedure: str, options: dict[str, Any] | None = None):
        self._request_id = request_id
        self._procedure = procedure
        self._options = {} if options is None else options

    @property
    def request_id(self) -> int:
        return self._request_id

    @property
    def procedure(self) -> str:
        return self._procedure

    @property
    def options(self) -> dict[str, Any]:
        return self._options


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
            3: util.validate_procedure,
        },
    )

    def __init__(self, fields: IRegisterFields):
        super().__init__()
        self._fields = fields

    @property
    def request_id(self) -> int:
        return self._fields.request_id

    @property
    def procedure(self) -> str:
        return self._fields.procedure

    @property
    def options(self) -> dict[str, Any]:
        return self._fields.options

    @classmethod
    def parse(cls, msg: list[Any]) -> Register:
        f = util.validate_message(msg, cls.TYPE, cls.VALIDATION_SPEC)
        return Register(RegisterFields(f.request_id, f.procedure, f.options))

    def marshal(self) -> list[Any]:
        return [self.TYPE, self.request_id, self.options, self.procedure]
