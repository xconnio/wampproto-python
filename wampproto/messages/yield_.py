from __future__ import annotations

from typing import Any

from wampproto.messages import util, exceptions
from wampproto.messages.message import Message


class Yield(Message):
    TEXT = "YIELD"
    TYPE = 70

    def __init__(
        self,
        request_id: int,
        args: list | None = None,
        kwargs: dict | None = None,
        options: dict | None = None,
    ):
        super().__init__()
        self.request_id = request_id
        self.args = args
        self.kwargs = kwargs
        self.options = options if options is not None else {}

    @classmethod
    def parse(cls, msg: list[Any]) -> Yield:
        util.sanity_check(msg, 3, 5, cls.TYPE, cls.TEXT)

        request_id = util.validate_session_id_or_raise(msg[1], cls.TEXT, "request ID")
        options = util.validate_details_or_raise(msg[2], cls.TEXT, "options")

        args = None
        if len(msg) > 3:
            args = msg[3]
            if not isinstance(args, list):
                raise exceptions.InvalidTypeError(list, type(msg[3]), "args", cls.TEXT)

        kwargs = None
        if len(msg) > 4:
            kwargs = msg[4]
            if not isinstance(kwargs, dict):
                raise exceptions.InvalidTypeError(dict, type(msg[4]), "kwargs", cls.TEXT)

        return Yield(request_id, args, kwargs, options)

    def marshal(self) -> list[Any]:
        message = [self.TYPE, self.request_id, self.options]
        if self.args is not None:
            message.append(self.args)

        if self.kwargs is not None:
            if self.args is None:
                message.append([])

            message.append(self.kwargs)

        return message
