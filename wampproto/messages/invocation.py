from __future__ import annotations

from typing import Any

from wampproto.messages import util
from wampproto.messages.message import Message, BinaryPayload
from wampproto.messages.validation_spec import ValidationSpec


class IInvocationFields(BinaryPayload):
    @property
    def request_id(self):
        raise NotImplementedError

    @property
    def registration_id(self):
        raise NotImplementedError

    @property
    def args(self):
        raise NotImplementedError

    @property
    def kwargs(self):
        raise NotImplementedError

    @property
    def details(self):
        raise NotImplementedError


class InvocationFields(IInvocationFields):
    def __init__(
        self,
        request_id: int,
        registration_id: int,
        args: list | None = None,
        kwargs: dict | None = None,
        details: dict | None = None,
        serializer: int | None = None,
        payload: bytes | None = None,
        binary: bool = False,
    ):
        super().__init__()
        self._request_id = request_id
        self._registration_id = registration_id
        self._args = args
        self._kwargs = kwargs
        self._details = {} if details is None else details

        self._serializer = serializer
        self._payload = payload
        self._binary = binary

    @property
    def request_id(self) -> int:
        return self._request_id

    @property
    def registration_id(self) -> int:
        return self._registration_id

    @property
    def args(self) -> list | None:
        return self._args

    @property
    def kwargs(self) -> dict[str, Any] | None:
        return self._kwargs

    @property
    def details(self) -> dict[str, Any]:
        return self._details

    def payload_is_binary(self) -> bool:
        return self._binary

    @property
    def payload(self) -> bytes | None:
        return self._payload

    @property
    def payload_serializer(self) -> int:
        return self._serializer


class Invocation(Message):
    TEXT = "INVOCATION"
    TYPE = 68

    VALIDATION_SPEC = ValidationSpec(
        min_length=4,
        max_length=6,
        message=TEXT,
        spec={
            1: util.validate_request_id,
            2: util.validate_registration_id,
            3: util.validate_details,
            4: util.validate_args,
            5: util.validate_kwargs,
        },
    )

    def __init__(self, fields: IInvocationFields):
        super().__init__()
        self._fields = fields

    @property
    def request_id(self) -> int:
        return self._fields.request_id

    @property
    def registration_id(self) -> int:
        return self._fields.registration_id

    @property
    def args(self) -> list | None:
        return self._fields.args

    @property
    def kwargs(self) -> dict[str, Any] | None:
        return self._fields.kwargs

    @property
    def details(self) -> dict[str, Any]:
        if self.payload_serializer is not None:
            self._fields.details["x_payload_serializer"] = self._fields.payload_serializer

        return self._fields.details

    def payload_is_binary(self) -> bool:
        return self._fields.payload_is_binary()

    @property
    def payload(self) -> bytes | None:
        return self._fields.payload

    @property
    def payload_serializer(self) -> int:
        return self._fields.payload_serializer

    @classmethod
    def parse(cls, msg: list[Any]) -> Invocation:
        f = util.validate_message(msg, cls.TYPE, cls.VALIDATION_SPEC)
        return Invocation(InvocationFields(f.request_id, f.registration_id, f.args, f.kwargs, f.details))

    def marshal(self) -> list[Any]:
        message = [self.TYPE, self.request_id, self.registration_id, self.details]
        if self.args is not None:
            message.append(self.args)

        if self.kwargs is not None:
            if self.args is None:
                message.append([])

            message.append(self.kwargs)

        return message
