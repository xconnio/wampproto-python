from __future__ import annotations

from typing import Any

from wampproto.messages import util, Message


class Interrupt(Message):
    TEXT = "INTERRUPT"
    TYPE = 69
    MIN_LENGTH = 3
    MAX_LENGTH = 3

    def __init__(
        self,
        inv_request_id: int,
        options: dict | None = None,
    ):
        super().__init__()
        self.inv_request_id = inv_request_id
        self.options = options if options is not None else {}

    @staticmethod
    def parse(msg: list[Any]) -> Interrupt:
        util.sanity_check(msg, Interrupt.MIN_LENGTH, Interrupt.MAX_LENGTH, Interrupt.TYPE, Interrupt.TEXT)

        request_id = util.validate_session_id_or_raise(msg[1], Interrupt.TEXT, "invocation request ID")
        options = util.validate_details_or_raise(msg[2], Interrupt.TEXT, "options")

        return Interrupt(request_id, options)

    def marshal(self) -> list[Any]:
        return [Interrupt.TYPE, self.inv_request_id, self.options]
