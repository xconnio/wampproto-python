from __future__ import annotations

from typing import Any

from wampproto.messages import util, exceptions
from wampproto.messages.message import Message


class Hello(Message):
    TEXT = "HELLO"
    TYPE = 1

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
        util.sanity_check(msg, 3, 3, Hello.TYPE, Hello.TEXT)

        realm = util.validate_realm_or_raise(msg[1], Hello.TEXT)
        details = util.validate_details_or_raise(msg[2], Hello.TEXT)

        roles = details.get("roles", {})
        if not isinstance(roles, dict):
            raise exceptions.ProtocolError(f"invalid type for 'roles' in details for {Hello.TEXT}")

        if len(roles) == 0:
            raise exceptions.ProtocolError(f"roles are missing in details for {Hello.TEXT}")

        for role in roles.keys():
            if role not in util.AllowedRoles.__members__.values():
                raise exceptions.ProtocolError(f"invalid role '{role}' in 'roles' details for {Hello.TEXT}")

        authid = details.get("authid", None)
        if authid is not None:
            if not isinstance(authid, str):
                raise exceptions.ProtocolError(f"authid must be a type string for {Hello.TEXT}")

        authrole = details.get("authrole", None)
        if authrole is not None:
            if not isinstance(authrole, str):
                raise exceptions.ProtocolError(f"authrole must be a type string for {Hello.TEXT}")

        authmethods = details.get("authmethods", None)
        if authmethods is not None:
            if not isinstance(authmethods, list):
                raise exceptions.InvalidTypeError(list, type(authmethods), "authmethods", Hello.TEXT)

            for authmethod in authmethods:
                if not isinstance(authmethod, str):
                    raise exceptions.InvalidTypeError(
                        str, type(authmethod), f"item '{authmethod}' in 'authmethods'", Hello.TEXT
                    )

        authextra = details.get("authextra", None)
        if authextra is not None:
            if not isinstance(authextra, dict):
                raise exceptions.InvalidTypeError(dict, type(authextra), "authextra", Hello.TEXT)

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

        return [self.TYPE, self.realm, details]
