from enum import Enum
from typing import Any

from wampproto.messages import exceptions
from wampproto.messages.validation_spec import ValidationSpec


MIN_ID = 1
MAX_ID = 2**53
INT = "int"
STRING = "string"
LIST = "list"
DICT = "dict"


class AllowedRoles(str, Enum):
    CALLEE = "callee"
    CALLER = "caller"
    PUBLISHER = "publisher"
    SUBSCRIBER = "subscriber"
    DEALER = "dealer"
    BROKER = "broker"

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


def validate_procedure_or_raise(procedure: str, error_msg: str) -> str:
    if procedure is None:
        raise exceptions.InvalidUriError(f"procedure cannot be null for {error_msg}")

    if not isinstance(procedure, str):
        raise exceptions.InvalidUriError(f"procedure must be of type string for {error_msg}")

    return procedure


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
        self.procedure: str | None = None
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
        return exceptions.InvalidDataTypeError.format(
            message=message, index=index, expected_type=INT, actual_type=type(value).__name__
        )

    return None


def validate_string_or_raise(value: str, index: int, message: str):
    if not isinstance(value, str):
        return exceptions.InvalidDataTypeError.format(
            message=message, index=index, expected_type=STRING, actual_type=type(value).__name__
        )

    return None


def validate_list_or_raise(value: str, index: int, message: str):
    if not isinstance(value, list):
        return exceptions.InvalidDataTypeError.format(
            message=message, index=index, expected_type=LIST, actual_type=type(value).__name__
        )

    return None


def validate_dict_or_raise(value: dict[str, Any], index: int, message: str):
    if not isinstance(value, dict):
        return exceptions.InvalidDataTypeError.format(
            message=message, index=index, expected_type=DICT, actual_type=type(value).__name__
        )

    return None


def validate_id_or_raise(value: int, index: int, message: str) -> str | None:
    if (error := validate_int_or_raise(value, index, message)) is not None:
        return error
    elif value < MIN_ID or value > MAX_ID:
        return exceptions.InvalidRangeError.format(message=message, index=index, start=MIN_ID, end=MAX_ID, actual=value)

    return None


def validate_request_id(msg: list[Any], index: int, fields: Fields, message: str) -> str | None:
    if (error := validate_id_or_raise(msg[index], index, message)) is not None:
        return error

    fields.request_id = msg[index]
    return None


def validate_uri(msg: list[Any], index: int, fields: Fields, name: str):
    if (error := validate_string_or_raise(msg[index], index, name)) is not None:
        return error

    fields.uri = msg[index]
    return None


def validate_procedure(msg: list[Any], index: int, fields: Fields, name: str):
    if (error := validate_string_or_raise(msg[index], index, name)) is not None:
        return error

    fields.procedure = msg[index]
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


def validate_authid(details: dict[str, Any], index: int, fields: Fields, name: str):
    if (authid := details.get("authid", None)) is not None:
        if validate_string_or_raise(authid, index, name) is not None:
            return exceptions.InvalidDetailError.format(
                message=name, index=index, key="authid", expected_type=STRING, actual_type=type(authid).__name__
            )

    fields.authid = authid
    return None


def validate_authrole(details: dict[str, Any], index: int, fields: Fields, name: str):
    if (authrole := details.get("authrole", None)) is not None:
        if validate_string_or_raise(authrole, index, name) is not None:
            return exceptions.InvalidDetailError.format(
                message=name, index=index, key="authrole", expected_type=STRING, actual_type=type(authrole).__name__
            )

    fields.authrole = authrole
    return None


def validate_authmethod(msg: list[Any], index: int, fields: Fields, name: str):
    if (error := validate_string_or_raise(msg[index], index, name)) is not None:
        return error

    fields.authmethod = msg[index]
    return None


def validate_authmethods(details: dict[str, Any], index: int, fields: Fields, name: str):
    authmethods = details.get("authmethods", None)
    if authmethods is not None:
        if validate_list_or_raise(authmethods, index, name) is not None:
            return exceptions.InvalidDetailError.format(
                message=name, index=index, key="authmethods", expected_type=LIST, actual_type=type(authmethods).__name__
            )

    fields.authmethods = authmethods
    return None


def validate_welcome_authmethod(details: dict[str, Any], index: int, fields: Fields, name: str):
    if (authmethod := details.get("authmethod", None)) is not None:
        if validate_string_or_raise(authmethod, index, name) is not None:
            return exceptions.InvalidDetailError.format(
                message=name, index=index, key="authmethod", expected_type=STRING, actual_type=type(authmethod).__name__
            )

    fields.authmethod = authmethod
    return None


def validate_authextra(details: dict[str, Any], index: int, fields: Fields, name: str):
    authextra = details.get("authextra", None)
    if authextra is not None:
        if validate_dict_or_raise(authextra, index, name) is not None:
            return exceptions.InvalidDetailError.format(
                message=name, index=index, key="authextra", expected_type=DICT, actual_type=type(authextra).__name__
            )

    fields.authextra = authextra
    return None


def validate_roles(details: dict[str, Any], index: int, fields: Fields, name: str):
    roles = details.get("roles", None)
    if validate_dict_or_raise(roles, index, name) is not None:
        return exceptions.InvalidDetailError.format(
            message=name, index=index, key="roles", expected_type=DICT, actual_type=type(roles).__name__
        )

    if len(roles) == 0:
        return (
            f"{name}: value at index {index} for roles key must be in {AllowedRoles.get_allowed_roles()} but was empty"
        )

    for role in roles:
        if role not in AllowedRoles.get_allowed_roles():
            return (
                f"{name}: value at index {index} for roles key must be in {AllowedRoles.get_allowed_roles()} "
                f"but was {role}"
            )

    fields.roles = roles
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


def validate_hello_details(msg: list[Any], index: int, fields: Fields, name: str):
    errors = []
    if (error := validate_dict_or_raise(msg[index], index, name)) is not None:
        return error

    if (error := validate_authid(msg[index], index, fields, name)) is not None:
        errors.append(error)

    if (error := validate_authrole(msg[index], index, fields, name)) is not None:
        errors.append(error)

    if (error := validate_authmethods(msg[index], index, fields, name)) is not None:
        errors.append(error)

    if (error := validate_roles(msg[index], index, fields, name)) is not None:
        errors.append(error)

    if (error := validate_authextra(msg[index], index, fields, name)) is not None:
        errors.append(error)

    if len(errors) > 0:
        return errors

    fields.details = msg[index]
    return None


def validate_welcome_details(msg: list[Any], index: int, fields: Fields, name: str):
    errors = []
    if (error := validate_dict_or_raise(msg[index], index, name)) is not None:
        return error

    if (error := validate_roles(msg[index], index, fields, name)) is not None:
        errors.append(error)

    if (error := validate_authid(msg[index], index, fields, name)) is not None:
        errors.append(error)

    if (error := validate_authrole(msg[index], index, fields, name)) is not None:
        errors.append(error)

    if (error := validate_authextra(msg[index], index, fields, name)) is not None:
        errors.append(error)

    if (error := validate_welcome_authmethod(msg[index], index, fields, name)) is not None:
        errors.append(error)

    if len(errors) > 0:
        return errors

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


def validate_message(msg: list[Any], type_: int, val_spec: ValidationSpec) -> Fields:
    sanity_check(msg, val_spec.min_length, val_spec.max_length, type_, val_spec.message)

    errors = []
    f = Fields()
    for idx, func in val_spec.spec.items():
        if (error := func(msg, idx, f, val_spec.message)) is not None:
            errors.append(error) if isinstance(error, str) else errors.extend(error)

    if len(errors) != 0:
        raise ValueError(*errors)

    return f
