from __future__ import annotations

from typing import Any

from wampproto.messages import util
from wampproto.messages.message import Message, BinaryPayload
from wampproto.messages.validation_spec import ValidationSpec


class IEventFields(BinaryPayload):
    @property
    def subscription_id(self):
        raise NotImplementedError

    @property
    def publication_id(self):
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


class EventFields(IEventFields):
    def __init__(
        self,
        subscription_id: int,
        publication_id: int,
        args: list | None = None,
        kwargs: dict[str, Any] | None = None,
        details: dict[str, Any] | None = None,
    ):
        super().__init__()
        self._subscription_id = subscription_id
        self._publication_id = publication_id
        self._args = args
        self._kwargs = kwargs
        self._details = {} if details is None else details

    @property
    def subscription_id(self) -> int:
        return self._subscription_id

    @property
    def publication_id(self) -> int:
        return self._publication_id

    @property
    def args(self) -> list[Any] | None:
        return self._args

    @property
    def kwargs(self) -> dict[str, Any] | None:
        return self._kwargs

    @property
    def details(self) -> dict[str, Any]:
        return self._details

    def payload_is_binary(self) -> bool:
        return False

    @property
    def payload(self) -> bytes | None:
        return None

    @property
    def payload_serializer(self) -> int:
        return 0


class Event(Message):
    TEXT = "EVENT"
    TYPE = 36

    VALIDATION_SPEC = ValidationSpec(
        min_length=4,
        max_length=6,
        message=TEXT,
        spec={
            1: util.validate_subscription_id,
            2: util.validate_publication_id,
            3: util.validate_details,
            4: util.validate_args,
            5: util.validate_kwargs,
        },
    )

    def __init__(self, fields: IEventFields):
        super().__init__()
        self._fields = fields

    @property
    def subscription_id(self) -> int:
        return self._fields.subscription_id

    @property
    def publication_id(self) -> int:
        return self._fields.publication_id

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
    def parse(cls, msg: list[Any]) -> Event:
        f = util.validate_message(msg, cls.TYPE, cls.VALIDATION_SPEC)
        return Event(EventFields(f.subscription_id, f.publication_id, f.args, f.kwargs, f.details))

    def marshal(self) -> list[Any]:
        message = [self.TYPE, self.subscription_id, self.publication_id, self.details]
        if self.args is not None:
            message.append(self.args)

        if self.kwargs is not None:
            if self.args is None:
                message.append([])

            message.append(self.kwargs)

        return message
