from __future__ import annotations

from typing import Any

from wamp.messages import error, util
from wamp.messages.message import Message


class Hello(Message):
    HELLO_TEXT = "HELLO"
    MESSAGE_TYPE = 1

    def __init__(
        self,
        realm: str,
        roles: dict[str, Any],
        authid: str | None = None,
        authrole: str | None = None,
    ):
        super().__init__()
        self.realm = realm
        self.roles = roles
        self.authid = authid
        self.authrole = authrole

    @staticmethod
    def parse(msg: list) -> Hello:
        if len(msg) != 3:
            raise error.ProtocolError(
                f"Invalid message length '{len(msg)}' for {Hello.HELLO_TEXT}, length should be equal to three"
            )

        if msg[0] != Hello.MESSAGE_TYPE:
            raise error.ProtocolError("Invalid message type for {Hello.HELLO_TEXT}")

        realm = util.validate_realm_or_raise(msg[1], Hello.HELLO_TEXT)
        details = util.validate_details_or_raise(msg[2], Hello.HELLO_TEXT)

        roles = details.get("roles", {})
        if len(roles) == 0:
            raise error.ProtocolError(f"roles are missing in details for {Hello.HELLO_TEXT}")

        for role in roles.keys():
            if role not in util.AllowedRoles.__members__.values():
                raise error.ProtocolError(f"Invalid role '{role}' in 'roles' details for {Hello.HELLO_TEXT}")

        authid = details.get("authid", None)
        if authid is not None:
            if not isinstance(authid, str):
                raise error.ProtocolError(f"authid must be a string type for {Hello.HELLO_TEXT}")

        authrole = details.get("authrole", None)
        if authrole is not None:
            if not isinstance(authrole, str):
                raise error.ProtocolError(f"authrole must be a string for {Hello.HELLO_TEXT}")

        return Hello(realm=realm, roles=roles, authid=authid, authrole=authrole)

    def marshal(self):
        details: dict[str, Any] = {"roles": self.roles}

        if self.authid is not None:
            details["authid"] = self.authid

        if self.authrole is not None:
            details["authrole"] = self.authrole

        return [self.MESSAGE_TYPE, self.realm, details]
