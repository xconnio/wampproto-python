from __future__ import annotations

from wamp.messages import error, util
from wamp.messages.message import Message


class Abort(Message):
    ABORT_TEXT = "ABORT"
    MESSAGE_TYPE = 3

    def __init__(self, details: dict, reason: str):
        super().__init__()
        self.details = details
        self.reason = reason

    @staticmethod
    def parse(msg: list) -> Abort:
        util.validate_message_or_raise(msg, Abort.ABORT_TEXT)

        if msg[0] != Abort.MESSAGE_TYPE:
            raise error.ProtocolError(f"invalid message type for {Abort.ABORT_TEXT}")

        details = util.validate_details_or_raise(msg[1], Abort.ABORT_TEXT)

        reason = util.validate_uri_or_raise(msg[2], Abort.ABORT_TEXT)

        return Abort(details, reason)

    def marshal(self):
        return [Abort.MESSAGE_TYPE, self.details, self.reason]
