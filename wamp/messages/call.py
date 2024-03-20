from __future__ import annotations

from typing import Any

from wamp.messages.message import Message
from wamp.messages import error, util


class Call(Message):
    Call_TEXT = "CALL"
    MESSAGE_TYPE = 48

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

    @staticmethod
    def parse(msg: list[Any]) -> Call:
        if not isinstance(msg, list):
            raise error.InvalidTypeError(list, type(msg), "message", Call.Call_TEXT)

        if len(msg) < 4 or len(msg) > 6:
            raise error.InvalidMessageLengthError("between 4 & 6", len(msg), Call.Call_TEXT)

        if msg[0] != Call.MESSAGE_TYPE:
            raise error.InvalidMessageTypeError(Call.MESSAGE_TYPE, msg[0], Call.Call_TEXT)

        request_id = util.validate_session_id_or_raise(msg[1], Call.Call_TEXT, "request ID")
        options = util.validate_details_or_raise(msg[2], Call.Call_TEXT, "options")
        uri = util.validate_uri_or_raise(msg[3], Call.Call_TEXT)

        args = None
        if len(msg) > 4:
            args = msg[4]
            if not isinstance(args, list):
                raise error.InvalidTypeError(list, type(msg[4]), "args", Call.Call_TEXT)

        kwargs = None
        if len(msg) > 5:
            kwargs = msg[5]
            if not isinstance(kwargs, dict):
                raise error.InvalidTypeError(dict, type(msg[5]), "kwargs", Call.Call_TEXT)

        return Call(request_id, uri, args, kwargs, options)

    def marshal(self) -> list[Any]:
        message = [Call.MESSAGE_TYPE, self.request_id, self.options, self.uri]
        if self.args is not None:
            message.append(self.args)

        if self.kwargs is not None:
            message.append(self.kwargs)

        return message
