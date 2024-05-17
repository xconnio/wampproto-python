from enum import Enum
from typing import Any

from wampproto.messages import exceptions
from wampproto.messages.validation_spec import ValidationSpec


MIN_ID = 1
MAX_ID = 9007199254740992
INT = "int"
STRING = "string"
LIST = "list"
DICT = "dictionary"


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


class Fields:
    def __init__(self):
        super().__init__()
        self.request_id: int | None = None
        self.uri: str | None = None
        self.args: list[Any] | None = None
        self.kwargs: dict[str, Any] | None = None

        self.session_id: int | None = None

        self.realm: str | None = None
        self.authid: str | None = None
        self.authrole: str | None = None
        self.authmethod: str | None = None
        self.authmethods: list[str] | None = None
        self.authextra: dict[str, Any] | None = None
        self.roles: dict[str, Any] | None = None

        self.message_type: int | None = None
        self.signature: str | None = None
        self.reason: str | None = None
        self.topic: str | None = None

        self.extra: dict[str, Any] | None = None
        self.options: dict[str, Any] | None = None
        self.details: dict[str, Any] | None = None

        self.subscription_id: int | None = None
        self.publication_id: int | None = None

        self.registration_id: int | None = None


def validate_int_or_raise(value: int, index: int, message: str):
    if not isinstance(value, int):
        return exceptions.InvalidDataTypeError(message, index, INT, type(value).__name__)

    return None


def validate_string_or_raise(value: str, index: int, message: str):
    if not isinstance(value, str):
        return exceptions.InvalidDataTypeError(message, index, STRING, type(value).__name__)

    return None


def validate_list_or_raise(value: str, index: int, message: str):
    if not isinstance(value, list):
        return exceptions.InvalidDataTypeError(message, index, LIST, type(value).__name__)

    return None


def validate_dict_or_raise(value: dict[str, Any], index: int, message: str):
    if not isinstance(value, dict):
        return exceptions.InvalidDataTypeError(message, index, DICT, type(value).__name__)

    return None


def validate_id_or_raise(
    value: int, index: int, message: str
) -> exceptions.InvalidDataTypeError | exceptions.InvalidRangeError | None:
    if (error := validate_int_or_raise(value, index, message)) is not None:
        return error
    elif value < MIN_ID or value > MAX_ID:
        return exceptions.InvalidRangeError(message, index, MIN_ID, MAX_ID, value)

    return None


def validate_request_id(
    msg: list[Any], index: int, fields: Fields, message: str
) -> exceptions.InvalidDataTypeError | exceptions.InvalidRangeError | None:
    if (error := validate_id_or_raise(msg[index], index, message)) is not None:
        return error

    fields.request_id = msg[index]
    return None


def validate_uri(msg: list[Any], index: int, fields: Fields, name: str):
    if (error := validate_string_or_raise(msg[index], index, name)) is not None:
        return error

    fields.uri = msg[index]
    return None


def validate_args(msg: list[Any], index: int, fields: Fields, name: str):
    if len(msg) > index:
        if (error := validate_list_or_raise(msg[index], index, name)) is not None:
            return error

        fields.args = msg[index]
        return None


def validate_kwargs(msg: list[Any], index: int, fields: Fields, name: str):
    if len(msg) > index:
        if (error := validate_dict_or_raise(msg[index], index, name)) is not None:
            return error

        fields.kwargs = msg[index]
        return None


def validate_session_id(msg: list[Any], index: int, fields: Fields, name: str) -> None:
    if (error := validate_id_or_raise(msg[index], index, name)) is not None:
        return error

    fields.session_id = msg[index]
    return None


def validate_realm(msg: list[Any], index: int, fields: Fields, name: str):
    if (error := validate_string_or_raise(msg[index], index, name)) is not None:
        return error

    fields.realm = msg[index]
    return None


def validate_authid(msg: list[Any], index: int, fields: Fields, name: str):
    if (error := validate_string_or_raise(msg[index], index, name)) is not None:
        return error

    fields.authid = msg[index]
    return None


def validate_authrole(msg: list[Any], index: int, fields: Fields, name: str):
    if (error := validate_string_or_raise(msg[index], index, name)) is not None:
        return error

    fields.authrole = msg[index]
    return None


def validate_authmethod(msg: list[Any], index: int, fields: Fields, name: str):
    if (error := validate_string_or_raise(msg[index], index, name)) is not None:
        return error

    fields.authmethod = msg[index]
    return None


def validate_authmethods(msg: list[Any], index: int, fields: Fields, name: str):
    if (error := validate_list_or_raise(msg[index], index, name)) is not None:
        return error

    fields.authmethods = msg[index]
    return None


def validate_authextra(msg: list[Any], index: int, fields: Fields, name: str):
    if (error := validate_dict_or_raise(msg[index], index, name)) is not None:
        return error

    fields.authextra = msg[index]
    return None


def validate_roles(msg: list[Any], index: int, fields: Fields, name: str):
    if (error := validate_dict_or_raise(msg[index], index, name)) is not None:
        return error

    fields.roles = msg[index]
    return None


def validate_message_type(msg: list[Any], index: int, fields: Fields, name: str):
    if (error := validate_int_or_raise(msg[index], index, name)) is not None:
        return error

    fields.message_type = msg[index]
    return None


def validate_signature(msg: list[Any], index: int, fields: Fields, name: str):
    if (error := validate_string_or_raise(msg[index], index, name)) is not None:
        return error

    fields.signature = msg[index]
    return None


def validate_reason(msg: list[Any], index: int, fields: Fields, name: str):
    if (error := validate_string_or_raise(msg[index], index, name)) is not None:
        return error

    fields.reason = msg[index]
    return None


def validate_topic(msg: list[Any], index: int, fields: Fields, name: str):
    if (error := validate_string_or_raise(msg[index], index, name)) is not None:
        return error

    fields.topic = msg[index]
    return None


def validate_extra(msg: list[Any], index: int, fields: Fields, name: str):
    if (error := validate_dict_or_raise(msg[index], index, name)) is not None:
        return error

    fields.extra = msg[index]
    return None


def validate_options(msg: list[Any], index: int, fields: Fields, name: str):
    if (error := validate_dict_or_raise(msg[index], index, name)) is not None:
        return error

    fields.options = msg[index]
    return None


def validate_details(msg: list[Any], index: int, fields: Fields, name: str):
    if (error := validate_dict_or_raise(msg[index], index, name)) is not None:
        return error

    fields.details = msg[index]
    return None


def validate_subscription_id(msg: list[Any], index: int, fields: Fields, name: str):
    if (error := validate_id_or_raise(msg[index], index, name)) is not None:
        return error

    fields.subscription_id = msg[index]
    return None


def validate_publication_id(msg: list[Any], index: int, fields: Fields, name: str):
    if (error := validate_id_or_raise(msg[index], index, name)) is not None:
        return error

    fields.publication_id = msg[index]
    return None


def validate_registration_id(msg: list[Any], index: int, fields: Fields, name: str):
    if (error := validate_id_or_raise(msg[index], index, name)) is not None:
        return error

    fields.registration_id = msg[index]
    return None


def validate_message(msg: list[Any], type_: int, name: str, val_spec: ValidationSpec) -> Fields:
    sanity_check(msg, val_spec.min_length, val_spec.max_length, type_, name)

    errors = []
    f = Fields()
    for idx, func in val_spec.spec.items():
        if (error := func(msg, idx, f, val_spec.message)) is not None:
            errors.append(error)

    if len(errors) != 0:
        raise ValueError(errors)

    return f
