from __future__ import annotations

from typing import Any


class Message:
    TYPE = None
    TEXT = None

    @classmethod
    def parse(cls, msg: list[Any]) -> Message:
        raise NotImplementedError()

    def marshal(self) -> list[Any]:
        raise NotImplementedError()


class BinaryPayload:
    def payload_is_binary(self) -> bool:
        raise NotImplementedError()

    @property
    def payload(self) -> bytes | None:
        raise NotImplementedError()

    @property
    def payload_serializer(self) -> int:
        raise NotImplementedError()
