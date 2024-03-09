from typing import Any


class ProtocolError(Exception):
    pass


class InvalidRealmError(Exception):
    pass


class InvalidDetailsError(Exception):
    pass


class InvalidUriError(Exception):
    pass


class InvalidTypeError(Exception):
    def __init__(self, expected_type: Any, actual_type: Any, field: str, message_name: str):
        error_msg = f"invalid type: expected type '{expected_type.__name__}', got '{actual_type.__name__}' for {field} in '{message_name}'"
        super().__init__(error_msg)
