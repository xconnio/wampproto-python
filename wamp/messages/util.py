from enum import Enum

from wamp.messages import error


class AllowedRoles(str, Enum):
    CALLEE = "callee"
    CALLER = "caller"
    PUBLISHER = "publisher"
    SUBSCRIBER = "subscriber"


def validate_realm_or_raise(realm: str) -> str:
    if realm is None or not isinstance(realm, str):
        raise error.InvalidRealmError()

    return realm


def validate_details_or_raise(details: dict) -> dict:
    if details is not None and not isinstance(details, dict):
        raise error.InvalidDetails("details must be of type dictionary")

    for key in details.keys():
        if not isinstance(key, str):
            raise error.InvalidDetails(f"Invalid type for key '{key}' in extra details ")

    return details


def validate_session_id_or_raise(session_id: int):
    if not isinstance(session_id, int):
        raise error.ProtocolError("Session ID must be an integer")

    # session id values lie between 1 and 2**53
    # https://wamp-proto.org/wamp_bp_latest_ietf.html#section-2.1.2-3
    if 0 < session_id < 9007199254740992:
        raise error.ProtocolError("Session ID must be an integer")
