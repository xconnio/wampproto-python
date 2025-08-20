import pytest

from wampproto import messages
from wampproto.messages import util


def test_parse_with_invalid_type():
    message = "msg"
    with pytest.raises(ValueError) as exc_info:
        messages.Result.parse(message)

    assert (
        str(exc_info.value)
        == f"invalid message type {type(message).__name__} for {messages.Result.TEXT}, type should be a list"
    )


def test_parse_with_invalid_list_min_length():
    message = ["foo"]
    with pytest.raises(ValueError) as exc_info:
        messages.Result.parse(message)

    assert str(exc_info.value) == "invalid message length 1, must be at least 3"


def test_parse_with_invalid_list_max_length():
    message = ["foo", 12, 34, 1, 3, 2]
    with pytest.raises(ValueError) as exc_info:
        messages.Result.parse(message)

    assert str(exc_info.value) == "invalid message length 6, must be at most 5"


def test_parse_with_invalid_message_type():
    msg_type = 11
    message = [msg_type, 7814135, {}]
    with pytest.raises(ValueError) as exc_info:
        messages.Result.parse(message)

    assert (
        str(exc_info.value)
        == f"invalid message id {msg_type} for {messages.Result.TEXT}, expected {messages.Result.TYPE}"
    )


def test_parse_with_negative_request_id():
    message = [messages.Result.TYPE, -2, {}]
    with pytest.raises(ValueError) as exc_info:
        messages.Result.parse(message)

    assert (
        str(exc_info.value)
        == f"{messages.Result.TEXT}: value at index 1 must be between '{util.MIN_ID}' and '{util.MAX_ID}' but was -2"
    )


def test_parse_with_out_of_range_request_value():
    value = 9007199254740993
    message = [messages.Result.TYPE, value, {}]
    with pytest.raises(ValueError) as exc_info:
        messages.Result.parse(message)

    assert (
        str(exc_info.value)
        == f"{messages.Result.TEXT}: value at index 1 must be between '{util.MIN_ID}' and '{util.MAX_ID}' "
        f"but was {value}"
    )


def test_parse_with_invalid_details_type():
    message = [messages.Result.TYPE, 367, "details"]
    with pytest.raises(ValueError) as exc_info:
        messages.Result.parse(message)

    assert str(exc_info.value) == f"{messages.Result.TEXT}: value at index 2 must be of type '{util.DICT}' but was str"


def test_parse_with_invalid_args_type():
    message = [messages.Result.TYPE, 361, {}, "args"]
    with pytest.raises(ValueError) as exc_info:
        messages.Result.parse(message)

    assert str(exc_info.value) == f"{messages.Result.TEXT}: value at index 3 must be of type '{util.LIST}' but was str"


def test_parse_with_invalid_kwargs_type():
    message = [messages.Result.TYPE, 367, {}, [], ["kwargs"]]
    with pytest.raises(ValueError) as exc_info:
        messages.Result.parse(message)

    assert str(exc_info.value) == f"{messages.Result.TEXT}: value at index 4 must be of type '{util.DICT}' but was list"


def test_parse_correctly():
    request_id = 367
    message = [messages.Result.TYPE, request_id, {}]
    yield_message = messages.Result.parse(message)

    assert isinstance(yield_message, messages.Result)

    assert isinstance(yield_message.request_id, int)
    assert yield_message.request_id == request_id

    assert yield_message.args is None
    assert yield_message.kwargs is None
    assert yield_message.details == {}


def test_parse_correctly_with_details():
    request_id = 362
    details = {"caller_authid": "mahad"}
    message = [messages.Result.TYPE, request_id, details]
    yield_message = messages.Result.parse(message)

    assert isinstance(yield_message, messages.Result)

    assert isinstance(yield_message.request_id, int)
    assert yield_message.request_id == request_id

    assert isinstance(yield_message.details, dict)
    assert yield_message.details == details

    assert yield_message.args is None
    assert yield_message.kwargs is None


def test_parse_correctly_with_args():
    request_id = 367
    args = ["first", 2]
    message = [messages.Result.TYPE, request_id, {}, args]
    yield_message = messages.Result.parse(message)

    assert isinstance(yield_message, messages.Result)

    assert isinstance(yield_message.request_id, int)
    assert yield_message.request_id == request_id

    assert isinstance(yield_message.args, list)
    assert yield_message.args == args

    assert yield_message.details == {}
    assert yield_message.kwargs is None


def test_parse_correctly_with_kwargs():
    request_id = 367
    kwargs = {"name": "mahad"}
    message = [messages.Result.TYPE, request_id, {}, [], kwargs]
    result = messages.Result.parse(message)

    assert isinstance(result, messages.Result)

    assert isinstance(result.request_id, int)
    assert result.request_id == request_id

    assert result.kwargs == kwargs
    assert result.args == []
    assert result.details == {}


def test_parse_correctly_with_all_details():
    request_id = 3671
    details = {"caller_authid": "mahad"}
    args = ["arg1"]
    kwargs = {"name": "mahad"}
    message = [messages.Result.TYPE, request_id, details, args, kwargs]
    result = messages.Result.parse(message)

    assert isinstance(result, messages.Result)

    assert isinstance(result.request_id, int)
    assert result.request_id == request_id

    assert result.details == details
    assert result.args == args
    assert result.kwargs == kwargs


def test_marshal():
    request_id = 367
    message = messages.Result(messages.ResultFields(request_id)).marshal()

    assert isinstance(message, list)
    assert len(message) == 3

    assert isinstance(message[0], int)
    assert message[0] == messages.Result.TYPE

    assert isinstance(message[1], int)
    assert message[1] == request_id

    assert message[2] == {}


def test_marshal_with_args():
    request_id = 367
    args = ["new"]
    message = messages.Result(messages.ResultFields(request_id, args)).marshal()

    assert isinstance(message, list)
    assert len(message) == 4

    assert isinstance(message[0], int)
    assert message[0] == messages.Result.TYPE

    assert isinstance(message[1], int)
    assert message[1] == request_id

    assert message[2] == {}
    assert isinstance(message[3], list)
    assert message[3] == args


def test_marshal_with_kwargs():
    request_id = 167
    args = ["args"]
    kwargs = {"new": "value"}
    message = messages.Result(messages.ResultFields(request_id, args, kwargs)).marshal()

    assert isinstance(message, list)
    assert len(message) == 5

    assert isinstance(message[0], int)
    assert message[0] == messages.Result.TYPE

    assert isinstance(message[1], int)
    assert message[1] == request_id

    assert message[2] == {}

    assert isinstance(message[3], list)
    assert message[3] == args

    assert isinstance(message[4], dict)
    assert message[4] == kwargs


def test_marshal_with_all_details():
    request_id = 1677
    args = ["arg1"]
    kwargs = {"key": "value"}
    details = {"receive_progress": True}
    message = messages.Result(messages.ResultFields(request_id, args, kwargs, details)).marshal()

    assert isinstance(message, list)
    assert len(message) == 5

    assert isinstance(message[0], int)
    assert message[0] == messages.Result.TYPE

    assert isinstance(message[1], int)
    assert message[1] == request_id

    assert isinstance(message[2], dict)
    assert message[2] == details

    assert isinstance(message[3], list)
    assert message[3] == args

    assert isinstance(message[4], dict)
    assert message[4] == kwargs
