from enum import Enum
from typing import Any

from wampproto.messages import exceptions


class AllowedRoles(str, Enum):
    CALLEE = "callee"
    CALLER = "caller"
    PUBLISHER = "publisher"
    SUBSCRIBER = "subscriber"

    @classmethod
    def get_allowed_roles(cls) -> list[str]:
        return [e.value for e in AllowedRoles]


def validate_realm_or_raise(realm: str, error_msg: str) -> str:
    if realm is None:
        raise exceptions.InvalidRealmError(f"realm cannot be null for {error_msg}")

    if not isinstance(realm, str):
        raise exceptions.InvalidRealmError(f"realm must be of type string for {error_msg}")

    return realm


def validate_uri_or_raise(uri: str, error_msg: str) -> str:
    if uri is None:
        raise exceptions.InvalidUriError(f"uri cannot be null for {error_msg}")

    if not isinstance(uri, str):
        raise exceptions.InvalidUriError(f"uri must be of type string for {error_msg}")

    return uri


def validate_details_or_raise(details: dict[str, Any], error_msg: str, field: str | None = None) -> dict[str, Any]:
    if field is None:
        field = "details"
    if not isinstance(details, dict):
        raise exceptions.InvalidDetailsError(f"{field} must be of type dictionary for {error_msg}")

    for key in details.keys():
        if not isinstance(key, str):
            raise exceptions.InvalidDetailsError(f"invalid type for key '{key}' in extra details for {error_msg}")

    return details


def validate_session_id_or_raise(session_id: int, error_msg: str, field: str | None = None) -> int:
    if not isinstance(session_id, int):
        raise exceptions.ProtocolError(f"session ID must be an integer for {error_msg}")

    # session id values lie between 1 and 2**53
    # https://wamp-proto.org/wamp_bp_latest_ietf.html#section-2.1.2-3
    if session_id < 0 or session_id > 9007199254740992:
        if field is None:
            field = "Session ID"
        raise exceptions.ProtocolError(f"invalid {field} value for {error_msg}")

    return session_id


def sanity_check(wamp_message: list[Any], min_length: int, max_length: int, expected_id: int, name: str) -> None:
    if not isinstance(wamp_message, list):
        raise ValueError(f"invalid message type {type(wamp_message).__name__} for {name}, type should be a list")

    if len(wamp_message) < min_length:
        raise ValueError(f"invalid message length {len(wamp_message)}, must be at least {min_length}")

    if len(wamp_message) > max_length:
        raise ValueError(f"invalid message length {len(wamp_message)}, must be at most {max_length}")

    message_id = wamp_message[0]
    if message_id != expected_id:
        raise ValueError(f"invalid message id {message_id} for {name}, expected {expected_id}")
