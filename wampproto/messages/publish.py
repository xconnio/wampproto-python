from __future__ import annotations

from typing import Any

from wampproto.messages.message import Message
from wampproto.messages import util


class Publish(Message):
    TEXT = "PUBLISH"
    TYPE = 16

    def __init__(
        self,
        request_id: int,
        uri: str,
        args: list | None = None,
        kwargs: dict | None = None,
        options: dict | None = None,
    ):
        super().__init__()
        self.request_id = request_id
        self.uri = uri
        self.args = args
        self.kwargs = kwargs
        self.options = options if options is not None else {}

    @classmethod
    def parse(cls, msg: list[Any]) -> Publish:
        util.sanity_check(msg, 4, 6, cls.TYPE, cls.TEXT)

        request_id = util.validate_session_id_or_raise(msg[1], cls.TEXT, "request ID")
        options = util.validate_details_or_raise(msg[2], cls.TEXT, "options")
        uri = util.validate_uri_or_raise(msg[3], cls.TEXT)

        args = []
        if len(msg) > 4:
            args = msg[4]

        kwargs = {}
        if len(msg) > 5:
            kwargs = msg[5]

        return Publish(request_id, uri, args, kwargs, options)

    def marshal(self) -> list[Any]:
        message = [self.TYPE, self.request_id, self.options, self.uri]
        if self.args is not None:
            message.append(self.args)

        if self.kwargs is not None:
            if self.args is None:
                message.append([])

            message.append(self.kwargs)

        return message
