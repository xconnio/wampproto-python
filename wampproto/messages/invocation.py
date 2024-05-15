from __future__ import annotations

from typing import Any

from wampproto.messages import util, exceptions
from wampproto.messages.message import Message


class Invocation(Message):
    TEXT = "INVOCATION"
    TYPE = 68

    def __init__(
        self,
        request_id: int,
        registration_id: int,
        args: list | None = None,
        kwargs: dict | None = None,
        details: dict | None = None,
    ):
        super().__init__()
        self.request_id = request_id
        self.registration_id = registration_id
        self.args = args
        self.kwargs = kwargs
        self.details = details if details is not None else {}

    @classmethod
    def parse(cls, msg: list[Any]) -> Invocation:
        util.sanity_check(msg, 4, 6, cls.TYPE, cls.TEXT)

        request_id = util.validate_session_id_or_raise(msg[1], cls.TEXT, "request ID")
        registration_id = util.validate_session_id_or_raise(msg[2], cls.TEXT, "registration ID")
        options = util.validate_details_or_raise(msg[3], cls.TEXT, "options")

        args = None
        if len(msg) > 4:
            args = msg[4]
            if not isinstance(args, list):
                raise exceptions.InvalidTypeError(list, type(msg[4]), "args", cls.TEXT)

        kwargs = None
        if len(msg) > 5:
            kwargs = msg[5]
            if not isinstance(kwargs, dict):
                raise exceptions.InvalidTypeError(dict, type(msg[5]), "kwargs", cls.TEXT)

        return Invocation(request_id, registration_id, args, kwargs, options)

    def marshal(self) -> list[Any]:
        message = [self.TYPE, self.request_id, self.registration_id, self.details]
        if self.args is not None:
            message.append(self.args)

        if self.kwargs is not None:
            if self.args is None:
                message.append([])

            message.append(self.kwargs)

        return message
