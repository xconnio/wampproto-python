from __future__ import annotations

from typing import Any

from wampproto.messages import util
from wampproto.messages.message import Message
from wampproto.messages.validation_spec import ValidationSpec


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
            3: util.validate_options,
            4: util.validate_args,
            5: util.validate_kwargs,
        },
    )

    def __init__(
        self,
        subscription_id: int,
        publication_id: int,
        args: list | None = None,
        kwargs: dict | None = None,
        details: dict | None = None,
    ):
        super().__init__()
        self.subscription_id = subscription_id
        self.publication_id = publication_id
        self.args = args
        self.kwargs = kwargs
        self.details = details if details is not None else {}

    @classmethod
    def parse(cls, msg: list[Any]) -> Event:
        f = util.validate_message(msg, cls.TYPE, cls.TEXT, cls.VALIDATION_SPEC)
        return Event(f.subscription_id, f.publication_id, f.args, f.kwargs, f.options)

    def marshal(self) -> list[Any]:
        message = [self.TYPE, self.subscription_id, self.publication_id, self.details]
        if self.args is not None:
            message.append(self.args)

        if self.kwargs is not None:
            if self.args is None:
                message.append([])

            message.append(self.kwargs)

        return message
