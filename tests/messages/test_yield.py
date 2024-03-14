import pytest

from wamp import messages
from wamp.messages import error


def test_parse_with_invalid_type():
    message = 1
    with pytest.raises(error.InvalidTypeError) as exc_info:
        messages.Yield.parse(message)

    assert (
        str(exc_info.value)
        == f"invalid type: expected type 'list', got 'int' for message in '{messages.Yield.YIELD_TEXT}'"
    )


def test_parse_with_invalid_list_length():
    message = ["bar"]
    with pytest.raises(error.InvalidMessageLengthError) as exc_info:
        messages.Yield.parse(message)

    assert (
        str(exc_info.value)
        == f"invalid message length: expected length 'between 3 & 5', got '{len(message)}' for '{messages.Yield.YIELD_TEXT}'"
    )


def test_parse_with_invalid_message_type():
    msg_type = 11
    message = [msg_type, 7814135, {}]
    with pytest.raises(error.InvalidMessageTypeError) as exc_info:
        messages.Yield.parse(message)

    assert (
        str(exc_info.value) == f"invalid message type: "
        f"message type for {messages.Yield.YIELD_TEXT} is '{messages.Yield.MESSAGE_TYPE}', got '{msg_type}'"
    )


def test_parse_with_negative_request_id():
    message = [messages.Yield.MESSAGE_TYPE, -2, {}]
    with pytest.raises(error.ProtocolError) as exc_info:
        messages.Yield.parse(message)

    assert str(exc_info.value) == f"invalid request ID value for {messages.Yield.YIELD_TEXT}"


def test_parse_with_out_of_range_request_value():
    message = [messages.Yield.MESSAGE_TYPE, 9007199254740993, {}]
    with pytest.raises(error.ProtocolError) as exc_info:
        messages.Yield.parse(message)

    assert str(exc_info.value) == f"invalid request ID value for {messages.Yield.YIELD_TEXT}"


def test_parse_with_invalid_options_type():
    message = [messages.Yield.MESSAGE_TYPE, 367, "options"]
    with pytest.raises(error.InvalidDetailsError) as exc_info:
        messages.Yield.parse(message)

    assert str(exc_info.value) == f"options must be of type dictionary for {messages.Yield.YIELD_TEXT}"


def test_parse_with_invalid_options_dict_key():
    message = [messages.Yield.MESSAGE_TYPE, 367, {2: "v"}]
    with pytest.raises(error.InvalidDetailsError) as exc_info:
        messages.Yield.parse(message)

    assert str(exc_info.value) == f"invalid type for key '2' in extra details for {messages.Yield.YIELD_TEXT}"


def test_parse_with_invalid_args_type():
    message = [messages.Yield.MESSAGE_TYPE, 361, {}, "args"]
    with pytest.raises(error.InvalidTypeError) as exc_info:
        messages.Yield.parse(message)

    assert (
        str(exc_info.value) == f"invalid type: expected type 'list', got 'str' for args in '{messages.Yield.YIELD_TEXT}'"
    )


def test_parse_with_invalid_kwargs_type():
    message = [messages.Yield.MESSAGE_TYPE, 367, {}, [], ["kwargs"]]
    with pytest.raises(error.InvalidTypeError) as exc_info:
        messages.Yield.parse(message)

    assert (
        str(exc_info.value)
        == f"invalid type: expected type 'dict', got 'list' for kwargs in '{messages.Yield.YIELD_TEXT}'"
    )


def test_parse_correctly():
    request_id = 367
    message = [messages.Yield.MESSAGE_TYPE, request_id, {}]
    yield_message = messages.Yield.parse(message)

    assert isinstance(yield_message, messages.Yield)

    assert isinstance(yield_message.request_id, int)
    assert yield_message.request_id == request_id

    assert yield_message.args is None
    assert yield_message.kwargs is None
    assert yield_message.options == {}


def test_parse_correctly_with_options():
    request_id = 362
    options = {"caller_authid": "mahad"}
    message = [messages.Yield.MESSAGE_TYPE, request_id, options]
    yield_message = messages.Yield.parse(message)

    assert isinstance(yield_message, messages.Yield)

    assert isinstance(yield_message.request_id, int)
    assert yield_message.request_id == request_id

    assert isinstance(yield_message.options, dict)
    assert yield_message.options == options

    assert yield_message.args is None
    assert yield_message.kwargs is None


def test_parse_correctly_with_args():
    request_id = 367
    args = ["first", 2]
    message = [messages.Yield.MESSAGE_TYPE, request_id, {}, args]
    yield_message = messages.Yield.parse(message)

    assert isinstance(yield_message, messages.Yield)

    assert isinstance(yield_message.request_id, int)
    assert yield_message.request_id == request_id

    assert isinstance(yield_message.args, list)
    assert yield_message.args == args

    assert yield_message.options == {}
    assert yield_message.kwargs is None


def test_parse_correctly_with_kwargs():
    request_id = 367
    kwargs = {"name": "mahad"}
    message = [messages.Yield.MESSAGE_TYPE, request_id, {}, [], kwargs]
    yield_message = messages.Yield.parse(message)

    assert isinstance(yield_message, messages.Yield)

    assert isinstance(yield_message.request_id, int)
    assert yield_message.request_id == request_id

    assert yield_message.kwargs == kwargs
    assert yield_message.args == []
    assert yield_message.options == {}


def test_parse_correctly_with_all_options():
    request_id = 3671
    options = {"caller_authid": "mahad"}
    args = ["arg1"]
    kwargs = {"name": "mahad"}
    message = [messages.Yield.MESSAGE_TYPE, request_id, options, args, kwargs]
    yield_message = messages.Yield.parse(message)

    assert isinstance(yield_message, messages.Yield)

    assert isinstance(yield_message.request_id, int)
    assert yield_message.request_id == request_id

    assert yield_message.options == options
    assert yield_message.args == args
    assert yield_message.kwargs == kwargs


def test_marshal():
    request_id = 367
    message = messages.Yield(request_id).marshal()

    assert isinstance(message, list)
    assert len(message) == 3

    assert isinstance(message[0], int)
    assert message[0] == messages.Yield.MESSAGE_TYPE

    assert isinstance(message[1], int)
    assert message[1] == request_id

    assert message[2] == {}


def test_marshal_with_args():
    request_id = 367
    args = ["new"]
    message = messages.Yield(request_id, args).marshal()

    assert isinstance(message, list)
    assert len(message) == 4

    assert isinstance(message[0], int)
    assert message[0] == messages.Yield.MESSAGE_TYPE

    assert isinstance(message[1], int)
    assert message[1] == request_id

    assert message[2] == {}
    assert isinstance(message[3], list)
    assert message[3] == args


def test_marshal_with_kwargs():
    request_id = 167
    args = ["args"]
    kwargs = {"new": "value"}
    message = messages.Yield(request_id, args, kwargs).marshal()

    assert isinstance(message, list)
    assert len(message) == 5

    assert isinstance(message[0], int)
    assert message[0] == messages.Yield.MESSAGE_TYPE

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
    message = messages.Yield(request_id, args, kwargs, options).marshal()

    assert isinstance(message, list)
    assert len(message) == 5

    assert isinstance(message[0], int)
    assert message[0] == messages.Yield.MESSAGE_TYPE

    assert isinstance(message[1], int)
    assert message[1] == request_id

    assert isinstance(message[2], dict)
    assert message[2] == options

    assert isinstance(message[3], list)
    assert message[3] == args

    assert isinstance(message[4], dict)
    assert message[4] == kwargs
