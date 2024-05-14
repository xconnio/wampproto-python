from __future__ import annotations

from typing import Any


class Message:
    TYPE = None
    TEXT = None

    def __init__(
        self,
        uri: str | None = None,
        args: list[Any] | None = None,
        request_id: int | None = None,
        session_id: int | None = None,
        realm: str | None = None,
        authid: str | None = None,
        authrole: str | None = None,
        authmethod: str | None = None,
        authmethods: list[str] | None = None,
        roles: dict[str, Any] | None = None,
        message_type: int | None = None,
        signature: str | None = None,
        details: dict[str, Any] | None = None,
        reason: str | None = None,
        topic: str | None = None,
        extra: dict[str, Any] | None = None,
        kwargs: dict[str, Any] | None = None,
        options: dict[str, Any] | None = None,
        authextra: dict[str, Any] | None = None,
        subscription_id: int | None = None,
        publication_id: int | None = None,
        registration_id: int | None = None,
    ) -> None:
        self.uri = uri
        self.args = args
        self.request_id = request_id
        self.session_id = session_id

        self.realm = realm
        self.authid = authid
        self.authrole = authrole
        self.authmethod = authmethod
        self.authmethods = authmethods
        self.roles = roles

        self.message_type = message_type
        self.signature = signature
        self.details = details if details is not None else {}
        self.reason = reason
        self.topic = topic

        self.kwargs = kwargs
        self.extra = extra if extra is not None else {}
        self.options = options if options is not None else {}
        self.authextra = authextra

        self.subscription_id = subscription_id
        self.publication_id = publication_id

        self.registration_id = registration_id

    @staticmethod
    def parse(msg: list[Any]) -> Message:
        raise NotImplementedError()

    def marshal(self) -> list[Any]:
        raise NotImplementedError()
