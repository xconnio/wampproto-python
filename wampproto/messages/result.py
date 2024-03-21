from __future__ import annotations

from typing import Any

from wampproto.messages import util
from wampproto.messages import error
from wampproto.messages.message import Message


class Result(Message):
    RESULT_TEXT = "RESULT"
    MESSAGE_TYPE = 50

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

    @staticmethod
    def parse(msg: list[Any]) -> Result:
        util.sanity_check(msg, 3, 5, Result.MESSAGE_TYPE, Result.RESULT_TEXT)

        request_id = util.validate_session_id_or_raise(msg[1], Result.RESULT_TEXT, "request ID")
        options = util.validate_details_or_raise(msg[2], Result.RESULT_TEXT, "options")

        args = None
        if len(msg) > 3:
            args = msg[3]
            if not isinstance(args, list):
                raise error.InvalidTypeError(list, type(msg[3]), "args", Result.RESULT_TEXT)

        kwargs = None
        if len(msg) > 4:
            kwargs = msg[4]
            if not isinstance(kwargs, dict):
                raise error.InvalidTypeError(dict, type(msg[4]), "kwargs", Result.RESULT_TEXT)

        return Result(request_id, args, kwargs, options)

    def marshal(self) -> list[Any]:
        message = [Result.MESSAGE_TYPE, self.request_id, self.options]
        if self.args is not None:
            message.append(self.args)

        if self.kwargs is not None:
            message.append(self.kwargs)

        return message
