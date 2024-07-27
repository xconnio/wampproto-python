from __future__ import annotations

from typing import Any

from wampproto.messages import util
from wampproto.messages.message import Message, BinaryPayload
from wampproto.messages.validation_spec import ValidationSpec


class IResultFields(BinaryPayload):
    @property
    def request_id(self):
        raise NotImplementedError

    @property
    def options(self):
        raise NotImplementedError

    @property
    def args(self):
        raise NotImplementedError

    @property
    def kwargs(self):
        raise NotImplementedError


class ResultFields(IResultFields):
    def __init__(
        self,
        request_id: int,
        args: list | None = None,
        kwargs: dict | None = None,
        options: dict | None = None,
        payload: bytes | None = None,
        serializer: int | None = None,
    ):
        super().__init__()
        self._request_id = request_id
        self._args = args
        self._kwargs = kwargs
        self._options = {} if options is None else options

        self._serializer = serializer
        self._payload = payload

    @property
    def request_id(self) -> int:
        return self._request_id

    @property
    def options(self) -> dict[str, Any]:
        return self._options

    @property
    def args(self) -> list[Any] | None:
        return self._args

    @property
    def kwargs(self) -> dict[str, Any] | None:
        return self._kwargs

    def payload_is_binary(self) -> bool:
        return self._serializer != 0

    @property
    def payload(self) -> bytes | None:
        return self._payload

    @property
    def payload_serializer(self) -> int:
        return self._serializer


class Result(Message):
    TEXT = "RESULT"
    TYPE = 50

    VALIDATION_SPEC = ValidationSpec(
        min_length=3,
        max_length=5,
        message=TEXT,
        spec={
            1: util.validate_request_id,
            2: util.validate_options,
            3: util.validate_args,
            4: util.validate_kwargs,
        },
    )

    def __init__(self, fields: IResultFields):
        super().__init__()
        self._fields = fields

    @property
    def request_id(self) -> int:
        return self._fields.request_id

    @property
    def options(self) -> dict[str, Any]:
        return self._fields.options

    @property
    def args(self) -> list[Any] | None:
        return self._fields.args

    @property
    def kwargs(self) -> dict[str, Any] | None:
        return self._fields.kwargs

    def payload_is_binary(self) -> bool:
        return self._fields.payload_is_binary()

    @property
    def payload(self) -> bytes | None:
        return self._fields.payload

    @property
    def payload_serializer(self) -> int:
        return self._fields.payload_serializer

    @classmethod
    def parse(cls, msg: list[Any]) -> Result:
        f = util.validate_message(msg, cls.TYPE, cls.VALIDATION_SPEC)
        return Result(ResultFields(f.request_id, f.args, f.kwargs, f.options))

    def marshal(self) -> list[Any]:
        message = [self.TYPE, self.request_id, self.options]
        if self.args is not None:
            message.append(self.args)

        if self.kwargs is not None:
            if self.args is None:
                message.append([])

            message.append(self.kwargs)

        return message
