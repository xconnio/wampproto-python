from __future__ import annotations

from typing import Any

from wampproto.messages.message import Message
from wampproto.messages import util
from wampproto.messages.validation_spec import ValidationSpec


class IPublishedFields:
    @property
    def request_id(self):
        raise NotImplementedError

    @property
    def publication_id(self):
        raise NotImplementedError


class PublishedFields(IPublishedFields):
    def __init__(self, request_id: int, publication_id: int):
        self._request_id = request_id
        self._publication_id = publication_id

    @property
    def request_id(self) -> int:
        return self._request_id

    @property
    def publication_id(self) -> int:
        return self._publication_id


class Published(Message):
    TEXT = "PUBLISHED"
    TYPE = 17

    VALIDATION_SPEC = ValidationSpec(
        min_length=3,
        max_length=3,
        message=TEXT,
        spec={
            1: util.validate_request_id,
            2: util.validate_publication_id,
        },
    )

    def __init__(self, fields: IPublishedFields):
        super().__init__()
        self._fields = fields

    @property
    def request_id(self) -> int:
        return self._fields.request_id

    @property
    def publication_id(self) -> int:
        return self._fields.publication_id

    @classmethod
    def parse(cls, msg: list[Any]) -> Published:
        f = util.validate_message(msg, cls.TYPE, cls.VALIDATION_SPEC)
        return Published(PublishedFields(f.request_id, f.publication_id))

    def marshal(self) -> list[Any]:
        return [self.TYPE, self.request_id, self.publication_id]
