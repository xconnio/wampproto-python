from __future__ import annotations

from typing import Any

from wampproto.messages import util
from wampproto.messages.message import Message
from wampproto.messages.validation_spec import ValidationSpec


class Welcome(Message):
    TEXT = "WELCOME"
    TYPE = 2

    VALIDATION_SPEC = ValidationSpec(
        min_length=3,
        max_length=3,
        message=TEXT,
        spec={
            1: util.validate_session_id,
            2: util.validate_welcome_details,
        },
    )

    def __init__(
        self,
        session_id: int,
        roles: dict[str, Any],
        authid: str | None = None,
        authrole: str | None = None,
        authmethod: str | None = None,
        authextra: str | None = None,
    ):
        super().__init__()
        self.session_id = session_id
        self.roles = roles
        self.authid = authid
        self.authrole = authrole
        self.authmethod = authmethod
        self.authextra = authextra

    @classmethod
    def parse(cls, msg: list[Any]) -> Welcome:
        f = util.validate_message(msg, cls.TYPE, cls.TEXT, cls.VALIDATION_SPEC)
        return Welcome(
            session_id=f.session_id,
            roles=f.roles,
            authid=f.authid,
            authrole=f.authrole,
            authmethod=f.authmethod,
            authextra=f.authextra,
        )

    def marshal(self) -> list[Any]:
        details: dict[str, Any] = {"roles": self.roles}

        if self.authid is not None:
            details["authid"] = self.authid

        if self.authrole is not None:
            details["authrole"] = self.authrole

        if self.authmethod is not None:
            details["authmethod"] = self.authmethod

        if self.authextra is not None:
            details["authextra"] = self.authextra

        return [self.TYPE, self.session_id, details]
