from __future__ import annotations

from typing import Any

from wampproto.messages import util
from wampproto.messages.message import Message, BinaryPayload
from wampproto.messages.validation_spec import ValidationSpec


class ICallFields(BinaryPayload):
    @property
    def request_id(self):
        raise NotImplementedError()

    @property
    def options(self):
        raise NotImplementedError()

    @property
    def procedure(self):
        raise NotImplementedError()

    @property
    def args(self):
        raise NotImplementedError()

    @property
    def kwargs(self):
        raise NotImplementedError()


class CallFields(ICallFields):
    def __init__(
        self,
        request_id: int,
        procedure: str,
        args: list | None = None,
        kwargs: dict[str, Any] | None = None,
        options: dict[str, Any] | None = None,
        serializer: int | None = None,
        payload: bytes | None = None,
        binary: bool = False,
    ):
        super().__init__()
        self._request_id = request_id
        self._procedure = procedure
        self._args = args
        self._kwargs = kwargs
        self._options = {} if options is None else options

        self._serializer = serializer
        self._payload = payload
        self._binary = binary

    @property
    def request_id(self) -> int:
        return self._request_id

    @property
    def procedure(self) -> str:
        return self._procedure

    @property
    def args(self) -> list[Any] | None:
        return self._args

    @property
    def kwargs(self) -> dict[str, Any] | None:
        return self._kwargs

    @property
    def options(self) -> dict[str, Any]:
        return self._options

    def payload_is_binary(self) -> bool:
        return self._binary

    @property
    def payload(self) -> bytes | None:
        return self._payload

    @property
    def payload_serializer(self) -> int:
        return self._serializer


class Call(Message):
    TEXT = "CALL"
    TYPE = 48

    # index number mapped to validation interface
    VALIDATION_SPEC = ValidationSpec(
        min_length=4,
        max_length=6,
        message=TEXT,
        spec={
            1: util.validate_request_id,
            2: util.validate_options,
            3: util.validate_procedure,
            4: util.validate_args,
            5: util.validate_kwargs,
        },
    )

    def __init__(self, fields: ICallFields):
        super().__init__()
        self._fields = fields

    @property
    def request_id(self) -> int:
        return self._fields.request_id

    @property
    def procedure(self) -> str:
        return self._fields.procedure

    @property
    def args(self) -> list[Any] | None:
        return self._fields.args

    @property
    def kwargs(self) -> dict[str, Any] | None:
        return self._fields.kwargs

    @property
    def options(self) -> dict[str, Any]:
        if self.payload_serializer is not None:
            self._fields.options["x_payload_serializer"] = self._fields.payload_serializer

        return self._fields.options

    def payload_is_binary(self) -> bool:
        return self._fields.payload_is_binary()

    @property
    def payload(self) -> bytes | None:
        return self._fields.payload

    @property
    def payload_serializer(self) -> int:
        return self._fields.payload_serializer

    @classmethod
    def parse(cls, msg: list[Any]) -> Call:
        f = util.validate_message(msg, cls.TYPE, cls.VALIDATION_SPEC)
        return Call(CallFields(f.request_id, f.procedure, f.args, f.kwargs, f.options))

    def marshal(self) -> list[Any]:
        message = [self.TYPE, self.request_id, self.options, self.procedure]
        if self.args is not None:
            message.append(self.args)

        if self.kwargs is not None:
            if self.args is None:
                message.append([])

            message.append(self.kwargs)

        return message
