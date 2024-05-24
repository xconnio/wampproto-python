from __future__ import annotations

from typing import Any

from wampproto.messages import util
from wampproto.messages.message import Message
from wampproto.messages.validation_spec import ValidationSpec


class Result(Message):
    TEXT = "RESULT"
    TYPE = 50

    VALIDATION_SPEC = ValidationSpec(
        min_length=3,
        max_length=5,
        message=TEXT,
        spec={
            1: util.validate_request_id,
            2: util.validate_options,
            3: util.validate_args,
            4: util.validate_kwargs,
        },
    )

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
    def parse(cls, msg: list[Any]) -> Result:
        f = util.validate_message(msg, cls.TYPE, cls.TEXT, cls.VALIDATION_SPEC)
        return Result(f.request_id, f.args, f.kwargs, f.options)

    def marshal(self) -> list[Any]:
        message = [self.TYPE, self.request_id, self.options]
        if self.args is not None:
            message.append(self.args)

        if self.kwargs is not None:
            if self.args is None:
                message.append([])

            message.append(self.kwargs)

        return message
