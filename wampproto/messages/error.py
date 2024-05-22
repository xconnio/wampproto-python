from __future__ import annotations

from typing import Any

from wampproto.messages import util
from wampproto.messages.message import Message
from wampproto.messages.validation_spec import ValidationSpec


class Error(Message):
    TEXT = "ERROR"
    TYPE = 8

    VALIDATION_SPEC = ValidationSpec(
        min_length=5,
        max_length=7,
        message=TEXT,
        spec={
            1: util.validate_session_id,
            2: util.validate_request_id,
            3: util.validate_details,
            4: util.validate_uri,
            5: util.validate_args,
            6: util.validate_kwargs,
        },
    )

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
        f = util.validate_message(msg, cls.TYPE, cls.TEXT, cls.VALIDATION_SPEC)
        return Error(f.message_type, f.request_id, f.uri, f.args, f.kwargs, f.details)

    def marshal(self) -> list[Any]:
        message = [self.TYPE, self.message_type, self.request_id, self.details, self.uri]
        if self.args is not None:
            message.append(self.args)

        if self.kwargs is not None:
            if self.args is None:
                message.append([])

            message.append(self.kwargs)

        return message
