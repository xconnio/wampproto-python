from __future__ import annotations

from typing import Any

from wampproto.messages.message import Message
from wampproto.messages import util


class Published(Message):
    TEXT = "PUBLISHED"
    TYPE = 17

    def __init__(self, request_id: int, publication_id: int):
        super().__init__()
        self.request_id = request_id
        self.publication_id = publication_id

    @staticmethod
    def parse(msg: list[Any]) -> Published:
        util.sanity_check(msg, 3, 3, Published.TYPE, Published.TEXT)

        request_id = util.validate_session_id_or_raise(msg[1], Published.TEXT, "request ID")
        publication_id = util.validate_session_id_or_raise(msg[2], Published.TEXT, "publication ID")

        return Published(request_id, publication_id)

    def marshal(self) -> list[Any]:
        return [Published.TEXT, self.request_id, self.publication_id]
