from __future__ import annotations

from typing import Any

from wampproto.messages import util
from wampproto.messages.message import Message
from wampproto.messages.validation_spec import ValidationSpec


class IHelloFields:
    @property
    def realm(self) -> str:
        raise NotImplementedError()

    @property
    def roles(self) -> dict[str, Any]:
        raise NotImplementedError()

    @property
    def authid(self) -> str:
        raise NotImplementedError()

    @property
    def authmethods(self) -> list[str]:
        raise NotImplementedError()

    @property
    def authextra(self) -> dict:
        raise NotImplementedError()


class HelloFields(IHelloFields):
    def __init__(
        self,
        realm: str,
        roles: dict[str, Any],
        authid: str | None = None,
        authmethods: list[str] | None = None,
        authextra: dict | None = None,
    ):
        super().__init__()
        self._realm = realm
        self._roles = roles
        self._authid = authid
        self._authmethods = authmethods
        self._authextra = authextra

    @property
    def realm(self) -> str:
        return self._realm

    @property
    def roles(self) -> dict[str, Any]:
        return self._roles

    @property
    def authid(self) -> str:
        return self._authid

    @property
    def authmethods(self) -> list[str]:
        return self._authmethods

    @property
    def authextra(self) -> dict:
        return self._authextra


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

    def __init__(self, fields: IHelloFields):
        super().__init__()
        self._fields = fields

    @property
    def realm(self) -> str:
        return self._fields.realm

    @property
    def roles(self) -> dict[str, Any]:
        return self._fields.roles

    @property
    def authid(self) -> str:
        return self._fields.authid

    @property
    def authmethods(self) -> list[str]:
        return self._fields.authmethods

    @property
    def authextra(self) -> dict:
        return self._fields.authextra

    @classmethod
    def parse(cls, msg: list[Any]) -> Hello:
        f = util.validate_message(msg, cls.TYPE, cls.VALIDATION_SPEC)
        return Hello(
            HelloFields(
                realm=f.realm,
                roles=f.roles,
                authid=f.authid,
                authmethods=f.authmethods,
                authextra=f.authextra,
            )
        )

    def marshal(self) -> list[Any]:
        details: dict[str, Any] = {"roles": self.roles}

        if self.authid is not None:
            details["authid"] = self.authid

        if self.authmethods is not None:
            details["authmethods"] = self.authmethods

        if self.authextra is not None:
            details["authextra"] = self.authextra

        return [self.TYPE, self.realm, details]
