from __future__ import annotations

from typing import Any

from wampproto.messages import util
from wampproto.messages.message import Message, BinaryPayload
from wampproto.messages.validation_spec import ValidationSpec


class IErrorFields(BinaryPayload):
    @property
    def message_type(self):
        raise NotImplementedError

    @property
    def request_id(self):
        raise NotImplementedError

    @property
    def details(self):
        raise NotImplementedError

    @property
    def uri(self):
        raise NotImplementedError

    @property
    def args(self):
        raise NotImplementedError

    @property
    def kwargs(self):
        raise NotImplementedError


class ErrorFields(IErrorFields):
    def __init__(
        self,
        message_type: int,
        request_id: int,
        uri: str,
        args: list | None = None,
        kwargs: dict | None = None,
        details: dict | None = None,
    ):
        super().__init__()
        self._message_type = message_type
        self._request_id = request_id
        self._uri = uri
        self._args = args
        self._kwargs = kwargs
        self._details = {} if details is None else details

    @property
    def message_type(self) -> int:
        return self._message_type

    @property
    def request_id(self) -> int:
        return self._request_id

    @property
    def uri(self) -> str:
        return self._uri

    @property
    def args(self) -> list[Any] | None:
        return self._args

    @property
    def kwargs(self) -> dict[str, Any] | None:
        return self._kwargs

    @property
    def details(self):
        return self._details

    def payload_is_binary(self) -> bool:
        return False

    @property
    def payload(self) -> bytes | None:
        return None

    @property
    def payload_serializer(self) -> int:
        return 0


class Error(Message):
    TEXT = "ERROR"
    TYPE = 8

    VALIDATION_SPEC = ValidationSpec(
        min_length=5,
        max_length=7,
        message=TEXT,
        spec={
            1: util.validate_message_type,
            2: util.validate_request_id,
            3: util.validate_details,
            4: util.validate_uri,
            5: util.validate_args,
            6: util.validate_kwargs,
        },
    )

    def __init__(self, fields: IErrorFields):
        super().__init__()
        self._fields = fields

    @property
    def message_type(self) -> int:
        return self._fields.message_type

    @property
    def request_id(self) -> int:
        return self._fields.request_id

    @property
    def uri(self) -> str:
        return self._fields.uri

    @property
    def args(self) -> list[Any] | None:
        return self._fields.args

    @property
    def kwargs(self) -> dict[str, Any] | None:
        return self._fields.kwargs

    @property
    def details(self) -> dict[str, Any]:
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
    def parse(cls, msg: list[Any]) -> Error:
        f = util.validate_message(msg, cls.TYPE, cls.VALIDATION_SPEC)
        return Error(ErrorFields(f.message_type, f.request_id, f.uri, f.args, f.kwargs, f.details))

    def marshal(self) -> list[Any]:
        message = [self.TYPE, self.message_type, self.request_id, self.details, self.uri]
        if self.args is not None:
            message.append(self.args)

        if self.kwargs is not None:
            if self.args is None:
                message.append([])

            message.append(self.kwargs)

        return message

    def __str__(self) -> str:
        error = self.uri
        if self.args is not None:
            args = ", ".join(str(arg) for arg in self.args)
            error += f": {args}"
        if self.kwargs is not None:
            kwargs = ", ".join(f"{key}={value}" for key, value in self.kwargs.items())
            error += f": {kwargs}"

        return error
