from __future__ import annotations

from typing import Any

from wampproto.messages import util, exceptions
from wampproto.messages.message import Message
from wampproto.messages.validation_spec import ValidationSpec


class Hello(Message):
    TEXT = "HELLO"
    TYPE = 1

    VALIDATION_SPEC = ValidationSpec(
        min_length=3,
        max_length=3,
        message=TEXT,
        spec={
            1: util.validate_realm,
            2: util.validate_hello_details,
        },
    )

    def __init__(
        self,
        realm: str,
        roles: dict[str, Any],
        authid: str | None = None,
        authrole: str | None = None,
        authmethods: list[str] | None = None,
        authextra: dict | None = None,
    ):
        super().__init__()
        self.realm = realm
        self.roles = roles
        self.authid = authid
        self.authrole = authrole
        self.authmethods = authmethods
        self.authextra = authextra

    @classmethod
    def parse(cls, msg: list[Any]) -> Hello:
        f = util.validate_message(msg, cls.TYPE, cls.TEXT, cls.VALIDATION_SPEC)
        return Hello(
            realm=f.realm,
            roles=f.roles,
            authid=f.authid,
            authrole=f.authrole,
            authmethods=f.authmethods,
            authextra=f.authextra,
        )

    def marshal(self) -> list[Any]:
        details: dict[str, Any] = {"roles": self.roles}

        if self.authid is not None:
            details["authid"] = self.authid

        if self.authrole is not None:
            details["authrole"] = self.authrole

        if self.authmethods is not None:
            details["authmethods"] = self.authmethods

        if self.authextra is not None:
            details["authextra"] = self.authextra

        return [self.TYPE, self.realm, details]
