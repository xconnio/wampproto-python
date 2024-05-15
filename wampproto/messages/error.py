from __future__ import annotations

from typing import Any

from wampproto.messages.message import Message
from wampproto.messages import util, exceptions


class Error(Message):
    TEXT = "ERROR"
    TYPE = 8

    def __init__(
        self,
        message_type: int,
        request_id: int,
        uri: str,
        args: list | None = None,
        kwargs: dict | None = None,
        details: dict | None = None,
    ):
        super().__init__()
        self.message_type = message_type
        self.request_id = request_id
        self.uri = uri
        self.args = args
        self.kwargs = kwargs
        self.details = details if details is not None else {}

    @classmethod
    def parse(cls, msg: list[Any]) -> Error:
        util.sanity_check(msg, 5, 7, cls.TYPE, cls.TEXT)

        message_type = util.validate_session_id_or_raise(msg[1], cls.TEXT, "error ID")
        request_id = util.validate_session_id_or_raise(msg[2], cls.TEXT, "request ID")
        details = util.validate_details_or_raise(msg[3], cls.TEXT, "details")
        uri = util.validate_uri_or_raise(msg[4], cls.TEXT)

        args = None
        if len(msg) > 5:
            args = msg[5]
            if not isinstance(args, list):
                raise exceptions.InvalidTypeError(list, type(msg[5]), "args", cls.TEXT)

        kwargs = None
        if len(msg) == 7:
            kwargs = msg[6]
            if not isinstance(kwargs, dict):
                raise exceptions.InvalidTypeError(dict, type(msg[6]), "kwargs", cls.TEXT)

        return Error(message_type, request_id, uri, args, kwargs, details)

    def marshal(self) -> list[Any]:
        message = [self.TYPE, self.message_type, self.request_id, self.details, self.uri]
        if self.args is not None:
            message.append(self.args)

        if self.kwargs is not None:
            if self.args is None:
                message.append([])

            message.append(self.kwargs)

        return message
