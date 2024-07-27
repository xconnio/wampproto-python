from __future__ import annotations

from typing import Any

from wampproto.messages.message import Message
from wampproto.messages import util
from wampproto.messages.validation_spec import ValidationSpec


class IUnsubscribeFields:
    @property
    def request_id(self):
        raise NotImplementedError

    @property
    def subscription_id(self):
        raise NotImplementedError


class UnsubscribeFields(IUnsubscribeFields):
    def __init__(self, request_id: int, subscription_id: int):
        super().__init__()
        self._request_id = request_id
        self._subscription_id = subscription_id

    @property
    def request_id(self) -> int:
        return self._request_id

    @property
    def subscription_id(self) -> int:
        return self._subscription_id


class Unsubscribe(Message):
    TEXT = "UNSUBSCRIBE"
    TYPE = 34

    VALIDATION_SPEC = ValidationSpec(
        min_length=3,
        max_length=3,
        message=TEXT,
        spec={
            1: util.validate_request_id,
            2: util.validate_subscription_id,
        },
    )

    def __init__(self, fields: IUnsubscribeFields):
        super().__init__()
        self._fields = fields

    @property
    def request_id(self) -> int:
        return self._fields.request_id

    @property
    def subscription_id(self) -> int:
        return self._fields.subscription_id

    @classmethod
    def parse(cls, msg: list[Any]) -> Unsubscribe:
        f = util.validate_message(msg, cls.TYPE, cls.VALIDATION_SPEC)
        return Unsubscribe(UnsubscribeFields(f.request_id, f.subscription_id))

    def marshal(self) -> list[Any]:
        return [self.TYPE, self.request_id, self.subscription_id]
