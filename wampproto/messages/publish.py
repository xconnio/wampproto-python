from __future__ import annotations

from typing import Any

from wampproto.messages.message import Message
from wampproto.messages import util
from wampproto.messages.validation_spec import ValidationSpec


class IPublishFields:
    @property
    def request_id(self):
        raise NotImplementedError

    @property
    def options(self):
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


class PublishFields(IPublishFields):
    def __init__(
        self,
        request_id: int,
        uri: str,
        args: list | None = None,
        kwargs: dict | None = None,
        options: dict | None = None,
    ):
        super().__init__()
        self._request_id = request_id
        self._uri = uri
        self._args = args
        self._kwargs = kwargs
        self._options = {} if options is None else options

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
    def options(self) -> dict[str, Any]:
        return self._options


class Publish(Message):
    TEXT = "PUBLISH"
    TYPE = 16

    VALIDATION_SPEC = ValidationSpec(
        min_length=4,
        max_length=6,
        message=TEXT,
        spec={
            1: util.validate_request_id,
            2: util.validate_options,
            3: util.validate_uri,
            4: util.validate_args,
            5: util.validate_kwargs,
        },
    )

    def __init__(self, fields: IPublishFields):
        super().__init__()
        self._fields = fields

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
    def options(self) -> dict[str, Any]:
        return self._fields.options

    @classmethod
    def parse(cls, msg: list[Any]) -> Publish:
        f = util.validate_message(msg, cls.TYPE, cls.TEXT, cls.VALIDATION_SPEC)
        return Publish(PublishFields(f.request_id, f.uri, f.args, f.kwargs, f.options))

    def marshal(self) -> list[Any]:
        message = [self.TYPE, self.request_id, self.options, self.uri]
        if self.args is not None:
            message.append(self.args)

        if self.kwargs is not None:
            if self.args is None:
                message.append([])

            message.append(self.kwargs)

        return message
