from __future__ import annotations

from typing import Any

from wampproto.messages import util
from wampproto.messages import error
from wampproto.messages.message import Message


class Hello(Message):
    HELLO_TEXT = "HELLO"
    MESSAGE_TYPE = 1

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

    @staticmethod
    def parse(msg: list[Any]) -> Hello:
        util.sanity_check(msg, 3, 3, Hello.MESSAGE_TYPE, Hello.HELLO_TEXT)

        realm = util.validate_realm_or_raise(msg[1], Hello.HELLO_TEXT)
        details = util.validate_details_or_raise(msg[2], Hello.HELLO_TEXT)

        roles = details.get("roles", {})
        if not isinstance(roles, dict):
            raise error.ProtocolError(f"invalid type for 'roles' in details for {Hello.HELLO_TEXT}")

        if len(roles) == 0:
            raise error.ProtocolError(f"roles are missing in details for {Hello.HELLO_TEXT}")

        for role in roles.keys():
            if role not in util.AllowedRoles.__members__.values():
                raise error.ProtocolError(f"invalid role '{role}' in 'roles' details for {Hello.HELLO_TEXT}")

        authid = details.get("authid", None)
        if authid is not None:
            if not isinstance(authid, str):
                raise error.ProtocolError(f"authid must be a type string for {Hello.HELLO_TEXT}")

        authrole = details.get("authrole", None)
        if authrole is not None:
            if not isinstance(authrole, str):
                raise error.ProtocolError(f"authrole must be a type string for {Hello.HELLO_TEXT}")

        authmethods = details.get("authmethods", None)
        if authmethods is not None:
            if not isinstance(authmethods, list):
                raise error.InvalidTypeError(list, type(authmethods), "authmethods", Hello.HELLO_TEXT)

            for authmethod in authmethods:
                if not isinstance(authmethod, str):
                    raise error.InvalidTypeError(
                        str, type(authmethod), f"item '{authmethod}' in 'authmethods'", Hello.HELLO_TEXT
                    )

        authextra = details.get("authextra", None)
        if authextra is not None:
            if not isinstance(authextra, dict):
                raise error.InvalidTypeError(dict, type(authextra), "authextra", Hello.HELLO_TEXT)

        return Hello(
            realm=realm, roles=roles, authid=authid, authrole=authrole, authmethods=authmethods, authextra=authextra
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

        return [self.MESSAGE_TYPE, self.realm, details]
