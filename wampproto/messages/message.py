from typing import Any


class Message:
    TYPE = None

    @staticmethod
    def parse(msg: list[Any]) -> "Message":
        raise NotImplementedError()

    def marshal(self) -> list[Any]:
        raise NotImplementedError()
