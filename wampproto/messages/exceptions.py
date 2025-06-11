from typing import Any

InvalidDataTypeError = "{message}: value at index {index} must be of type '{expected_type}' but was {actual_type}"
InvalidRangeError = "{message}: value at index {index} must be between '{start}' and '{end}' but was {actual}"
InvalidDetailError = (
    "{message}: value at index {index} for key '{key}' must be of type '{expected_type}' but was {actual_type}"
)


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
        error_msg = (
            f"invalid type: expected type '{expected_type.__name__}', "
            f"got '{actual_type.__name__}' for {field} in '{message_name}'"
        )
        super().__init__(error_msg)


class InvalidMessageLengthError(Exception):
    def __init__(self, expected_length: str, actual_length: int, message_name: str):
        error_msg = (
            f"invalid message length: expected length '{expected_length}', got '{actual_length}' for '{message_name}'"
        )
        super().__init__(error_msg)


class InvalidMessageTypeError(Exception):
    def __init__(self, expected_type: int, actual_type: int, message_name: str):
        error_msg = f"invalid message type: message type for {message_name} is '{expected_type}', got '{actual_type}'"
        super().__init__(error_msg)
