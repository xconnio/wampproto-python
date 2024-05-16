from enum import Enum
from typing import Any

from wampproto.messages import exceptions
from wampproto.messages.validation_spec import ValidationSpec


MAX_ID = 9007199254740992


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


def validate_int_or_raise(value: int, field: str, name: str):
    if not isinstance(value, int):
        raise ValueError(f"invalid {field} '{value}' for {name}, type should be an integer")


def validate_string_or_raise(value: str, field: str, name: str):
    if not isinstance(value, str):
        raise ValueError(f"invalid {field} '{value}' for {name}, type should be a string")


def validate_list_or_raise(value: str, field: str, name: str):
    if not isinstance(value, list):
        raise ValueError(f"invalid {field} '{value}' for {name}, type should be a list")


def validate_dict_or_raise(value: dict[str, Any], field: str, name: str):
    if not isinstance(value, dict):
        raise ValueError(f"invalid {field} '{value}' for {name}, type should be a dictionary")

    for key in value.keys():
        if not isinstance(key, str):
            raise ValueError(f"invalid type for key {key} in {field} for {name}, key should be a string")


def validate_id_or_raise(value: int, field: str, name: str):
    validate_int_or_raise(value, field, name)
    if value < 0 or value > MAX_ID:
        raise ValueError(f"invalid {field} {value} for {name}, must be between 1 and {MAX_ID}")


def validate_request_id(msg: list[Any], index: int, fields: Fields, name: str) -> None:
    validate_id_or_raise(msg[index], "request ID", name)
    fields.request_id = msg[index]


def validate_uri(msg: list[Any], index: int, fields: Fields, name: str):
    validate_string_or_raise(msg[index], "uri", name)
    fields.uri = msg[index]


def validate_args(msg: list[Any], index: int, fields: Fields, name: str):
    if len(msg) > index:
        validate_list_or_raise(msg[index], "args", name)
        fields.args = msg[index]


def validate_kwargs(msg: list[Any], index: int, fields: Fields, name: str):
    if len(msg) > index:
        validate_dict_or_raise(msg[index], "kwargs", name)
        fields.kwargs = msg[index]


def validate_session_id(msg: list[Any], index: int, fields: Fields, name: str) -> None:
    validate_id_or_raise(msg[index], "session ID", name)
    fields.session_id = msg[index]


def validate_realm(msg: list[Any], index: int, fields: Fields, name: str):
    validate_string_or_raise(msg[index], "realm", name)
    fields.realm = msg[index]


def validate_authid(msg: list[Any], index: int, fields: Fields, name: str):
    validate_string_or_raise(msg[index], "authID", name)
    fields.authid = msg[index]


def validate_authrole(msg: list[Any], index: int, fields: Fields, name: str):
    validate_string_or_raise(msg[index], "authrole", name)
    fields.authrole = msg[index]


def validate_authmethod(msg: list[Any], index: int, fields: Fields, name: str):
    validate_string_or_raise(msg[index], "authmethod", name)
    fields.authmethod = msg[index]


def validate_authmethods(msg: list[Any], index: int, fields: Fields, name: str):
    validate_list_or_raise(msg[index], "authmethods", name)
    fields.authmethods = msg[index]


def validate_authextra(msg: list[Any], index: int, fields: Fields, name: str):
    validate_dict_or_raise(msg[index], "authextra", name)
    fields.authextra = msg[index]


def validate_roles(msg: list[Any], index: int, fields: Fields, name: str):
    validate_dict_or_raise(msg[index], "roles", name)
    fields.roles = msg[index]


def validate_message_type(msg: list[Any], index: int, fields: Fields, name: str):
    validate_int_or_raise(msg[index], "message_type", name)
    fields.message_type = msg[index]


def validate_signature(msg: list[Any], index: int, fields: Fields, name: str):
    validate_string_or_raise(msg[index], "signature", name)
    fields.signature = msg[index]


def validate_reason(msg: list[Any], index: int, fields: Fields, name: str):
    validate_string_or_raise(msg[index], "reason", name)
    fields.reason = msg[index]


def validate_topic(msg: list[Any], index: int, fields: Fields, name: str):
    validate_string_or_raise(msg[index], "topic", name)
    fields.topic = msg[index]


def validate_extra(msg: list[Any], index: int, fields: Fields, name: str):
    validate_dict_or_raise(msg[index], "extra", name)
    fields.extra = msg[index]


def validate_options(msg: list[Any], index: int, fields: Fields, name: str):
    validate_dict_or_raise(msg[index], "options", name)
    fields.options = msg[index]


def validate_details(msg: list[Any], index: int, fields: Fields, name: str):
    validate_dict_or_raise(msg[index], "details", name)
    fields.details = msg[index]


def validate_subscription_id(msg: list[Any], index: int, fields: Fields, name: str):
    validate_id_or_raise(msg[index], "subscription ID", name)
    fields.subscription_id = msg[index]


def validate_publication_id(msg: list[Any], index: int, fields: Fields, name: str):
    validate_id_or_raise(msg[index], "publication ID", name)
    fields.publication_id = msg[index]


def validate_registration_id(msg: list[Any], index: int, fields: Fields, name: str):
    validate_id_or_raise(msg[index], "registration ID", name)
    fields.registration_id = msg[index]


def validate_message(msg: list[Any], type_: int, name: str, val_spec: ValidationSpec) -> Fields:
    sanity_check(msg, val_spec.min_length, val_spec.max_length, type_, name)

    f = Fields()
    for idx, func in val_spec.spec.items():
        func(msg, idx, f, val_spec.message)

    return f
