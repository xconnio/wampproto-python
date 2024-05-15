from __future__ import annotations

from typing import Any

from wampproto.messages import util
from wampproto.messages.message import Message


class Event(Message):
    TEXT = "EVENT"
    TYPE = 36

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
        util.sanity_check(msg, 4, 6, cls.TYPE, cls.TEXT)

        subscription_id = util.validate_session_id_or_raise(msg[1], cls.TEXT, "subscription ID")
        publication_id = util.validate_session_id_or_raise(msg[2], cls.TEXT, "publication ID")
        options = util.validate_details_or_raise(msg[3], cls.TEXT, "options")

        args = []
        if len(msg) > 4:
            args = msg[4]

        kwargs = {}
        if len(msg) > 5:
            kwargs = msg[5]

        return Event(subscription_id, publication_id, args, kwargs, options)

    def marshal(self) -> list[Any]:
        message = [self.TYPE, self.subscription_id, self.publication_id, self.details]
        if self.args is not None:
            message.append(self.args)

        if self.kwargs is not None:
            if self.args is None:
                message.append([])

            message.append(self.kwargs)

        return message
