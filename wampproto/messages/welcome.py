from __future__ import annotations

from typing import Any

from wampproto.messages import util
from wampproto.messages.message import Message
from wampproto.messages.validation_spec import ValidationSpec


class IWelcomeFields:
    @property
    def session_id(self):
        raise NotImplementedError

    @property
    def roles(self):
        raise NotImplementedError

    @property
    def authid(self):
        raise NotImplementedError

    @property
    def authrole(self):
        raise NotImplementedError

    @property
    def authmethod(self):
        raise NotImplementedError

    @property
    def authextra(self):
        raise NotImplementedError


class WelcomeFields(IWelcomeFields):
    def __init__(
        self,
        session_id: int,
        roles: dict[str, Any],
        authid: str | None = None,
        authrole: str | None = None,
        authmethod: str | None = None,
        authextra: dict[str, Any] | None = None,
    ):
        super().__init__()
        self._session_id = session_id
        self._roles = roles
        self._authid = authid
        self._authrole = authrole
        self._authmethod = authmethod
        self._authextra = {} if authextra is None else authextra

    @property
    def session_id(self) -> int:
        return self._session_id

    @property
    def roles(self) -> dict[str, Any]:
        return self._roles

    @property
    def authid(self) -> str:
        return self._authid

    @property
    def authrole(self) -> str:
        return self._authrole

    @property
    def authmethod(self) -> str:
        return self._authmethod

    @property
    def authextra(self) -> dict[str, Any]:
        return self._authextra


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

    def __init__(self, fields: IWelcomeFields):
        super().__init__()
        self._fields = fields

    @property
    def session_id(self) -> int:
        return self._fields.session_id

    @property
    def roles(self) -> dict[str, Any]:
        return self._fields.roles

    @property
    def authid(self) -> str:
        return self._fields.authid

    @property
    def authrole(self) -> str:
        return self._fields.authrole

    @property
    def authmethod(self) -> str:
        return self._fields.authmethod

    @property
    def authextra(self) -> dict[str, Any]:
        return self._fields.authextra

    @classmethod
    def parse(cls, msg: list[Any]) -> Welcome:
        f = util.validate_message(msg, cls.TYPE, cls.VALIDATION_SPEC)
        return Welcome(
            WelcomeFields(
                session_id=f.session_id,
                roles=f.roles,
                authid=f.authid,
                authrole=f.authrole,
                authmethod=f.authmethod,
                authextra=f.authextra,
            )
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
