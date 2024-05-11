from __future__ import annotations

from typing import Any

from wampproto.messages import util, Message


class Cancel(Message):
    TEXT = "CANCEL"
    TYPE = 49
    MIN_LENGTH = 3
    MAX_LENGTH = 3

    def __init__(
        self,
        call_request_id: int,
        options: dict | None = None,
    ):
        super().__init__()
        self.call_request_id = call_request_id
        self.options = options if options is not None else {}

    @staticmethod
    def parse(msg: list[Any]) -> Cancel:
        util.sanity_check(msg, Cancel.MIN_LENGTH, Cancel.MAX_LENGTH, Cancel.TYPE, Cancel.TEXT)

        request_id = util.validate_session_id_or_raise(msg[1], Cancel.TEXT, "call request ID")
        options = util.validate_details_or_raise(msg[2], Cancel.TEXT, "options")

        return Cancel(request_id, options)

    def marshal(self) -> list[Any]:
        return [Cancel.TYPE, self.call_request_id, self.options]
