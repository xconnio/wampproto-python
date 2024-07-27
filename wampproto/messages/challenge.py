from __future__ import annotations

from typing import Any

from wampproto.messages import util
from wampproto.messages.message import Message
from wampproto.messages.validation_spec import ValidationSpec


class IChallengeFields:
    @property
    def authmethod(self):
        raise NotImplementedError()

    @property
    def extra(self):
        raise NotImplementedError()


class ChallengeFields(IChallengeFields):
    def __init__(self, authmethod: str, extra: dict[str, Any] | None = None):
        self._authmethod = authmethod
        self._extra = {} if extra is None else extra

    @property
    def authmethod(self) -> str:
        return self._authmethod

    @property
    def extra(self) -> dict[str, Any]:
        return self._extra


class Challenge(Message):
    TEXT = "CHALLENGE"
    TYPE = 4

    VALIDATION_SPEC = ValidationSpec(
        min_length=3,
        max_length=3,
        message=TEXT,
        spec={
            1: util.validate_authmethod,
            2: util.validate_extra,
        },
    )

    def __init__(self, fields: IChallengeFields):
        super().__init__()
        self._fields = fields

    @property
    def authmethod(self) -> str:
        return self._fields.authmethod

    @property
    def extra(self) -> dict[str, Any]:
        return self._fields.extra

    @classmethod
    def parse(cls, msg: list[Any]) -> Challenge:
        f = util.validate_message(msg, cls.TYPE, cls.VALIDATION_SPEC)
        return Challenge(ChallengeFields(f.authmethod, f.extra))

    def marshal(self) -> list[Any]:
        return [self.TYPE, self.authmethod, self.extra]
