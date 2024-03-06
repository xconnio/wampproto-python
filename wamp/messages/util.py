from enum import Enum
from typing import Any

from wamp.messages import error


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
        raise error.InvalidRealmError(f"realm cannot be null for {error_msg}")

    if not isinstance(realm, str):
        raise error.InvalidRealmError(f"realm must be of type string for {error_msg}")

    return realm


def validate_details_or_raise(details: dict[str, Any], error_msg: str) -> dict[str, Any]:
    if not isinstance(details, dict):
        raise error.InvalidDetailsError(f"details must be of type dictionary for {error_msg}")

    for key in details.keys():
        if not isinstance(key, str):
            raise error.InvalidDetailsError(f"invalid type for key '{key}' in extra details for {error_msg}")

    return details


def validate_session_id_or_raise(session_id: int, error_msg: str) -> int:
    if not isinstance(session_id, int):
        raise error.ProtocolError(f"session ID must be an integer for {error_msg}")

    # session id values lie between 1 and 2**53
    # https://wamp-proto.org/wamp_bp_latest_ietf.html#section-2.1.2-3
    if session_id < 0 or session_id > 9007199254740992:
        raise error.ProtocolError(f"invalid Session ID value for {error_msg}")

    return session_id
