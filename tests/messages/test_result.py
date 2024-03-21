import pytest

from wampproto.wamp import messages
from wampproto.wamp.messages import error


def test_parse_with_invalid_type():
    message = "msg"
    with pytest.raises(ValueError) as exc_info:
        messages.Result.parse(message)

    assert (
        str(exc_info.value)
        == f"invalid message type {type(message).__name__} for {messages.Result.RESULT_TEXT}, type should be a list"
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
        == f"invalid message id {msg_type} for {messages.Result.RESULT_TEXT}, expected {messages.Result.MESSAGE_TYPE}"
    )


def test_parse_with_negative_request_id():
    message = [messages.Result.MESSAGE_TYPE, -2, {}]
    with pytest.raises(error.ProtocolError) as exc_info:
        messages.Result.parse(message)

    assert str(exc_info.value) == f"invalid request ID value for {messages.Result.RESULT_TEXT}"


def test_parse_with_out_of_range_request_value():
    message = [messages.Result.MESSAGE_TYPE, 9007199254740993, {}]
    with pytest.raises(error.ProtocolError) as exc_info:
        messages.Result.parse(message)

    assert str(exc_info.value) == f"invalid request ID value for {messages.Result.RESULT_TEXT}"


def test_parse_with_invalid_options_type():
    message = [messages.Result.MESSAGE_TYPE, 367, "options"]
    with pytest.raises(error.InvalidDetailsError) as exc_info:
        messages.Result.parse(message)

    assert str(exc_info.value) == f"options must be of type dictionary for {messages.Result.RESULT_TEXT}"


def test_parse_with_invalid_options_dict_key():
    message = [messages.Result.MESSAGE_TYPE, 367, {2: "v"}]
    with pytest.raises(error.InvalidDetailsError) as exc_info:
        messages.Result.parse(message)

    assert str(exc_info.value) == f"invalid type for key '2' in extra details for {messages.Result.RESULT_TEXT}"


def test_parse_with_invalid_args_type():
    message = [messages.Result.MESSAGE_TYPE, 361, {}, "args"]
    with pytest.raises(error.InvalidTypeError) as exc_info:
        messages.Result.parse(message)

    assert (
        str(exc_info.value)
        == f"invalid type: expected type 'list', got 'str' for args in '{messages.Result.RESULT_TEXT}'"
    )


def test_parse_with_invalid_kwargs_type():
    message = [messages.Result.MESSAGE_TYPE, 367, {}, [], ["kwargs"]]
    with pytest.raises(error.InvalidTypeError) as exc_info:
        messages.Result.parse(message)

    assert (
        str(exc_info.value)
        == f"invalid type: expected type 'dict', got 'list' for kwargs in '{messages.Result.RESULT_TEXT}'"
    )


def test_parse_correctly():
    request_id = 367
    message = [messages.Result.MESSAGE_TYPE, request_id, {}]
    yield_message = messages.Result.parse(message)

    assert isinstance(yield_message, messages.Result)

    assert isinstance(yield_message.request_id, int)
    assert yield_message.request_id == request_id

    assert yield_message.args is None
    assert yield_message.kwargs is None
    assert yield_message.options == {}


def test_parse_correctly_with_options():
    request_id = 362
    options = {"caller_authid": "mahad"}
    message = [messages.Result.MESSAGE_TYPE, request_id, options]
    yield_message = messages.Result.parse(message)

    assert isinstance(yield_message, messages.Result)

    assert isinstance(yield_message.request_id, int)
    assert yield_message.request_id == request_id

    assert isinstance(yield_message.options, dict)
    assert yield_message.options == options

    assert yield_message.args is None
    assert yield_message.kwargs is None


def test_parse_correctly_with_args():
    request_id = 367
    args = ["first", 2]
    message = [messages.Result.MESSAGE_TYPE, request_id, {}, args]
    yield_message = messages.Result.parse(message)

    assert isinstance(yield_message, messages.Result)

    assert isinstance(yield_message.request_id, int)
    assert yield_message.request_id == request_id

    assert isinstance(yield_message.args, list)
    assert yield_message.args == args

    assert yield_message.options == {}
    assert yield_message.kwargs is None


def test_parse_correctly_with_kwargs():
    request_id = 367
    kwargs = {"name": "mahad"}
    message = [messages.Result.MESSAGE_TYPE, request_id, {}, [], kwargs]
    result = messages.Result.parse(message)

    assert isinstance(result, messages.Result)

    assert isinstance(result.request_id, int)
    assert result.request_id == request_id

    assert result.kwargs == kwargs
    assert result.args == []
    assert result.options == {}


def test_parse_correctly_with_all_options():
    request_id = 3671
    options = {"caller_authid": "mahad"}
    args = ["arg1"]
    kwargs = {"name": "mahad"}
    message = [messages.Result.MESSAGE_TYPE, request_id, options, args, kwargs]
    result = messages.Result.parse(message)

    assert isinstance(result, messages.Result)

    assert isinstance(result.request_id, int)
    assert result.request_id == request_id

    assert result.options == options
    assert result.args == args
    assert result.kwargs == kwargs


def test_marshal():
    request_id = 367
    message = messages.Result(request_id).marshal()

    assert isinstance(message, list)
    assert len(message) == 3

    assert isinstance(message[0], int)
    assert message[0] == messages.Result.MESSAGE_TYPE

    assert isinstance(message[1], int)
    assert message[1] == request_id

    assert message[2] == {}


def test_marshal_with_args():
    request_id = 367
    args = ["new"]
    message = messages.Result(request_id, args).marshal()

    assert isinstance(message, list)
    assert len(message) == 4

    assert isinstance(message[0], int)
    assert message[0] == messages.Result.MESSAGE_TYPE

    assert isinstance(message[1], int)
    assert message[1] == request_id

    assert message[2] == {}
    assert isinstance(message[3], list)
    assert message[3] == args


def test_marshal_with_kwargs():
    request_id = 167
    args = ["args"]
    kwargs = {"new": "value"}
    message = messages.Result(request_id, args, kwargs).marshal()

    assert isinstance(message, list)
    assert len(message) == 5

    assert isinstance(message[0], int)
    assert message[0] == messages.Result.MESSAGE_TYPE

    assert isinstance(message[1], int)
    assert message[1] == request_id

    assert message[2] == {}

    assert isinstance(message[3], list)
    assert message[3] == args

    assert isinstance(message[4], dict)
    assert message[4] == kwargs


def test_marshal_with_all_options():
    request_id = 1677
    args = ["arg1"]
    kwargs = {"key": "value"}
    options = {"receive_progress": True}
    message = messages.Result(request_id, args, kwargs, options).marshal()

    assert isinstance(message, list)
    assert len(message) == 5

    assert isinstance(message[0], int)
    assert message[0] == messages.Result.MESSAGE_TYPE

    assert isinstance(message[1], int)
    assert message[1] == request_id

    assert isinstance(message[2], dict)
    assert message[2] == options

    assert isinstance(message[3], list)
    assert message[3] == args

    assert isinstance(message[4], dict)
    assert message[4] == kwargs
