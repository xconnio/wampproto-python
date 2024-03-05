from __future__ import annotations

from typing import Any

from wamp.messages import error, util
from wamp.messages.message import Message


class Welcome(Message):
    MESSAGE_TYPE = 2

    def __init__(
        self,
        session_id: str,
        roles: dict[str, Any],
        authid: str | None = None,
        authrole: str | None = None,
    ):
        super().__init__(self)
        self.session_id = session_id
        self.roles = roles
        self.authid = authid
        self.authrole = authrole

    @staticmethod
    def serialize(msg: list) -> Welcome:
        if len(msg) != 3:
            raise error.ProtocolError(
                f"Invalid message length '{len(msg)}' for WELCOME, length should be equal to three"
            )

        if msg[0] != Welcome.MESSAGE_TYPE:
            raise error.ProtocolError("Invalid message type for WELCOME")

        session_id = util.validate_session_id_or_raise(msg[1])
        details = util.validate_details_or_raise(msg[2])

        roles = details.get("roles", {})
        if len(roles) == 0:
            raise error.ProtocolError("roles are missing in details for WELCOME")

        for role in roles.keys():
            if role not in util.AllowedRoles.__members__.values():
                raise error.ProtocolError(f"Invalid role '{role}' in 'roles' details for WELCOME")

        authid = details.get("authid", None)
        if authid is not None:
            if not isinstance(authid, str):
                raise error.ProtocolError("authid must be a string type for WELCOME")

        authrole = details.get("authrole", None)
        if authrole is not None:
            if not isinstance(authrole, str):
                raise error.ProtocolError("authrole must be a string")

        return Welcome(session_id=session_id, roles=roles, authid=authid, authrole=authrole)

    def deserialize(self):
        details: dict[str, Any] = {"roles": self.roles}

        if self.authid is not None:
            details["authid"] = self.authid

        if self.authrole is not None:
            details["authid"] = self.authid

        return [self.MESSAGE_TYPE, self.session_id, details]
