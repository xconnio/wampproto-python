from __future__ import annotations

from typing import Any

from wampproto.messages import util
from wampproto.messages.message import Message
from wampproto.messages.validation_spec import ValidationSpec


class Call(Message):
    TEXT = "CALL"
    TYPE = 48

    # index number mapped to validation interface
    VALIDATION_SPEC = ValidationSpec(
        min_length=4,
        max_length=6,
        spec={
            1: util.validate_request_id,
            2: util.validate_options,
            3: util.validate_uri,
            4: util.validate_args,
            5: util.validate_kwargs,
        },
    )

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
    def parse(cls, msg: list[Any]) -> Call:
        f = util.validate_message(msg, cls.TYPE, cls.TEXT, cls.VALIDATION_SPEC)
        return Call(f.request_id, f.uri, f.args, f.kwargs, f.options)

    def marshal(self) -> list[Any]:
        message = [self.TYPE, self.request_id, self.options, self.uri]
        if self.args is not None:
            message.append(self.args)

        if self.kwargs is not None:
            if self.args is None:
                message.append([])

            message.append(self.kwargs)

        return message
