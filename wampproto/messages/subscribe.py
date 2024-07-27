from __future__ import annotations

from typing import Any

from wampproto.messages.message import Message
from wampproto.messages import util
from wampproto.messages.validation_spec import ValidationSpec


class ISubscribeFields:
    @property
    def request_id(self):
        raise NotImplementedError

    @property
    def options(self):
        raise NotImplementedError

    @property
    def topic(self):
        raise NotImplementedError


class SubscribeFields(ISubscribeFields):
    def __init__(self, request_id: int, topic: str, options: dict[str, Any] | None = None):
        super().__init__()
        self._request_id = request_id
        self._topic = topic
        self._options = {} if options is None else options

    @property
    def request_id(self) -> int:
        return self._request_id

    @property
    def topic(self) -> str:
        return self._topic

    @property
    def options(self) -> dict[str, Any]:
        return self._options


class Subscribe(Message):
    TEXT = "SUBSCRIBE"
    TYPE = 32

    VALIDATION_SPEC = ValidationSpec(
        min_length=4,
        max_length=4,
        message=TEXT,
        spec={
            1: util.validate_request_id,
            2: util.validate_options,
            3: util.validate_topic,
        },
    )

    def __init__(self, fields: ISubscribeFields):
        super().__init__()
        self._fields = fields

    @property
    def request_id(self) -> int:
        return self._fields.request_id

    @property
    def topic(self) -> str:
        return self._fields.topic

    @property
    def options(self) -> dict[str, Any]:
        return self._fields.options

    @classmethod
    def parse(cls, msg: list[Any]) -> Subscribe:
        f = util.validate_message(msg, cls.TYPE, cls.VALIDATION_SPEC)
        return Subscribe(SubscribeFields(f.request_id, f.topic, f.options))

    def marshal(self) -> list[Any]:
        return [self.TYPE, self.request_id, self.options, self.topic]
