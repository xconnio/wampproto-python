from __future__ import annotations

from typing import Any

from wampproto.messages.message import Message
from wampproto.messages import util


class Register(Message):
    Register_Text = "REGISTER"
    MESSAGE_TYPE = 64

    def __init__(self, request_id: int, uri: str, options: dict = None):
        super().__init__()
        self.request_id = request_id
        self.uri = uri
        self.options = options

    @staticmethod
    def parse(msg: list[Any]) -> Register:
        util.sanity_check(msg, 4, 4, Register.MESSAGE_TYPE, Register.Register_Text)

        request_id = util.validate_session_id_or_raise(msg[1], Register.Register_Text, "request ID")
        options = util.validate_details_or_raise(msg[2], Register.Register_Text, "options")
        uri = util.validate_uri_or_raise(msg[3], Register.Register_Text)

        return Register(request_id, uri, options)

    def marshal(self) -> list[Any]:
        return [Register.MESSAGE_TYPE, self.request_id, self.options, self.uri]
