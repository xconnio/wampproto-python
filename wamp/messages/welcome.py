from __future__ import annotations

from typing import Any

from wamp.messages import error, util
from wamp.messages.message import Message


class Welcome(Message):
    WELCOME_TEXT = "WELCOME"
    MESSAGE_TYPE = 2

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

    @staticmethod
    def parse(msg: list) -> Welcome:
        if not isinstance(msg, list):
            raise error.ProtocolError(
                f"invalid message type '{type(msg)}' for {Welcome.WELCOME_TEXT}, type should be a list"
            )

        if len(msg) != 3:
            raise error.ProtocolError(
                f"invalid message length '{len(msg)}' for {Welcome.WELCOME_TEXT}, length should be equal to three"
            )

        if msg[0] != Welcome.MESSAGE_TYPE:
            raise error.ProtocolError("invalid message type for WELCOME")

        session_id = util.validate_session_id_or_raise(msg[1], Welcome.WELCOME_TEXT)
        details = util.validate_details_or_raise(msg[2], Welcome.WELCOME_TEXT)

        roles = details.get("roles", {})
        if not isinstance(roles, dict):
            raise error.ProtocolError(f"invalid type for 'roles' in details for {Welcome.WELCOME_TEXT}")

        if len(roles) == 0:
            raise error.ProtocolError(f"roles are missing in details for {Welcome.WELCOME_TEXT}")

        for role in roles.keys():
            if role not in util.AllowedRoles.__members__.values():
                raise error.ProtocolError(f"invalid role '{role}' in 'roles' details for {Welcome.WELCOME_TEXT}")

        authid = details.get("authid", None)
        if authid is not None:
            if not isinstance(authid, str):
                raise error.ProtocolError(f"authid must be a type string for {Welcome.WELCOME_TEXT}")

        authrole = details.get("authrole", None)
        if authrole is not None:
            if not isinstance(authrole, str):
                raise error.ProtocolError(f"authrole must be a type string for {Welcome.WELCOME_TEXT}")

        authmethod = details.get("authmethod", None)
        if authmethod is not None:
            if not isinstance(authmethod, str):
                raise error.InvalidTypeError(str, type(authmethod), "authmethod", Welcome.WELCOME_TEXT)

        authextra = details.get("authextra", None)
        if authextra is not None:
            if not isinstance(authextra, dict):
                raise error.InvalidTypeError(dict, type(authextra), "authextra", Welcome.WELCOME_TEXT)

        return Welcome(
            session_id=session_id,
            roles=roles,
            authid=authid,
            authrole=authrole,
            authmethod=authmethod,
            authextra=authextra,
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

        return [self.MESSAGE_TYPE, self.session_id, details]
