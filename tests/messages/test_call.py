import pytest

from wampproto import messages
from wampproto.messages import util, exceptions


def test_parse_with_invalid_type():
    message = "msg"
    with pytest.raises(ValueError) as exc_info:
        messages.Call.parse(message)

    assert str(exc_info.value) == f"invalid message type str for {messages.Call.TEXT}, type should be a list"


def test_parse_with_invalid_min_length():
    message = ["foo"]
    with pytest.raises(ValueError) as exc_info:
        messages.Call.parse(message)

    assert str(exc_info.value) == "invalid message length 1, must be at least 4"


def test_parse_with_invalid_max_length():
    message = ["foo", 1, 6, 3, 42, 24, 12]
    with pytest.raises(ValueError) as exc_info:
        messages.Call.parse(message)

    assert str(exc_info.value) == "invalid message length 7, must be at most 6"


def test_parse_with_invalid_message_type():
    msg_type = 10
    message = [msg_type, 7814135, {}, "io.xconn.ping"]
    with pytest.raises(ValueError) as exc_info:
        messages.Call.parse(message)

    assert str(exc_info.value) == f"invalid message id 10 for {messages.Call.TEXT}, expected {messages.Call.TYPE}"


def test_parse_with_multiple_errors():
    req_id = "1"
    options = 23
    uri = {"uri": "xconn"}
    message = [messages.Call.TYPE, req_id, options, uri]
    with pytest.raises(ValueError) as exc_info:
        messages.Call.parse(message)

    expected_errors = [
        exceptions.InvalidDataTypeError.format(
            message=messages.Call.TEXT, index=1, expected_type=util.INT, actual_type=type(req_id).__name__
        ),
        exceptions.InvalidDataTypeError.format(
            message=messages.Call.TEXT, index=2, expected_type=util.DICT, actual_type=type(options).__name__
        ),
        exceptions.InvalidDataTypeError.format(
            message=messages.Call.TEXT, index=3, expected_type=util.STRING, actual_type=type(uri).__name__
        ),
    ]

    assert str(exc_info.value) == str(ValueError(*expected_errors))


def test_parse_with_negative_request_id():
    message = [messages.Call.TYPE, -1, {}, "io.xconn.ping"]
    with pytest.raises(ValueError) as exc_info:
        messages.Call.parse(message)

    assert (
        str(exc_info.value)
        == f"{messages.Call.TEXT}: value at index 1 must be between '{util.MIN_ID}' and '{util.MAX_ID}' but was -1"
    )


def test_parse_with_out_of_range_request_value():
    req_id = 9007199254740993
    message = [messages.Call.TYPE, req_id, {}, "io.xconn.ping"]
    with pytest.raises(ValueError) as exc_info:
        messages.Call.parse(message)

    assert (
        str(exc_info.value)
        == f"{messages.Call.TEXT}: value at index 1 must be between '{util.MIN_ID}' and '{util.MAX_ID}' "
        f"but was {req_id}"
    )


def test_parse_with_invalid_options_type():
    message = [messages.Call.TYPE, 367, "options", "io.xconn.ping"]
    with pytest.raises(ValueError) as exc_info:
        messages.Call.parse(message)

    assert str(exc_info.value) == f"{messages.Call.TEXT}: value at index 2 must be of type 'dict' but was str"


def test_parse_with_uri_none():
    message = [messages.Call.TYPE, 367, {}, None]
    with pytest.raises(ValueError) as exc_info:
        messages.Call.parse(message)

    assert str(exc_info.value) == f"{messages.Call.TEXT}: value at index 3 must be of type 'string' but was NoneType"


def test_parse_with_invalid_uri_type():
    uri = {"uri": "io.xconn.ping"}
    message = [messages.Call.TYPE, 367, {}, uri]
    with pytest.raises(ValueError) as exc_info:
        messages.Call.parse(message)

    assert str(exc_info.value) == f"{messages.Call.TEXT}: value at index 3 must be of type 'string' but was dict"


def test_parse_with_invalid_args_type():
    message = [messages.Call.TYPE, 367, {}, "io.xconn.ping", "args"]
    with pytest.raises(ValueError) as exc_info:
        messages.Call.parse(message)

    assert str(exc_info.value) == f"{messages.Call.TEXT}: value at index 4 must be of type 'list' but was str"


def test_parse_with_invalid_kwargs_type():
    message = [messages.Call.TYPE, 367, {}, "io.xconn.ping", [], ["kwargs"]]
    with pytest.raises(ValueError) as exc_info:
        messages.Call.parse(message)

    assert str(exc_info.value) == f"{messages.Call.TEXT}: value at index 5 must be of type 'dict' but was list"


def test_parse_correctly():
    uri = "io.xconn.ping"
    request_id = 367
    message = [messages.Call.TYPE, request_id, {}, uri]
    call = messages.Call.parse(message)

    assert isinstance(call, messages.Call)

    assert isinstance(call.request_id, int)
    assert call.request_id == request_id

    assert isinstance(call.uri, str)
    assert call.uri == uri

    assert call.args is None
    assert call.kwargs is None
    assert call.options == {}


def test_parse_correctly_with_options():
    uri = "io.xconn.ping"
    request_id = 367
    options = {"caller_authid": "mahad"}
    message = [messages.Call.TYPE, request_id, options, uri]
    call = messages.Call.parse(message)

    assert isinstance(call, messages.Call)

    assert isinstance(call.request_id, int)
    assert call.request_id == request_id

    assert isinstance(call.uri, str)
    assert call.uri == uri

    assert isinstance(call.options, dict)
    assert call.options == options

    assert call.args is None
    assert call.kwargs is None


def test_parse_correctly_with_args():
    uri = "io.xconn.ping"
    request_id = 367
    args = ["first", 2]
    message = [messages.Call.TYPE, request_id, {}, uri, args]
    call = messages.Call.parse(message)

    assert isinstance(call, messages.Call)

    assert isinstance(call.request_id, int)
    assert call.request_id == request_id

    assert isinstance(call.uri, str)
    assert call.uri == uri

    assert isinstance(call.args, list)
    assert call.args == args

    assert call.options == {}
    assert call.kwargs is None


def test_parse_correctly_with_kwargs():
    uri = "io.xconn.ping"
    request_id = 367
    kwargs = {"name": "mahad"}
    message = [messages.Call.TYPE, request_id, {}, uri, [], kwargs]
    call = messages.Call.parse(message)

    assert isinstance(call, messages.Call)

    assert isinstance(call.request_id, int)
    assert call.request_id == request_id

    assert isinstance(call.uri, str)
    assert call.uri == uri

    assert call.kwargs == kwargs
    assert call.args == []
    assert call.options == {}


def test_parse_correctly_with_all_options():
    uri = "io.xconn.ping"
    request_id = 367
    options = {"caller_authid": "mahad"}
    args = ["arg1"]
    kwargs = {"name": "mahad"}
    message = [messages.Call.TYPE, request_id, options, uri, args, kwargs]
    call = messages.Call.parse(message)

    assert isinstance(call, messages.Call)

    assert isinstance(call.request_id, int)
    assert call.request_id == request_id

    assert isinstance(call.uri, str)
    assert call.uri == uri

    assert call.options == options
    assert call.args == args
    assert call.kwargs == kwargs


def test_marshal():
    request_id = 367
    uri = "io.xconn.hello"
    message = messages.Call(messages.CallFields(request_id, uri)).marshal()

    assert isinstance(message, list)
    assert len(message) == 4

    assert isinstance(message[0], int)
    assert message[0] == messages.Call.TYPE

    assert isinstance(message[1], int)
    assert message[1] == request_id

    assert message[2] == {}
    assert message[3] == uri


def test_marshal_with_args():
    request_id = 367
    uri = "io.xconn.hello"
    args = ["new"]
    message = messages.Call(messages.CallFields(request_id, uri, args)).marshal()

    assert isinstance(message, list)
    assert len(message) == 5

    assert isinstance(message[0], int)
    assert message[0] == messages.Call.TYPE

    assert isinstance(message[1], int)
    assert message[1] == request_id

    assert message[2] == {}
    assert message[3] == uri
    assert message[4] == args


def test_marshal_with_kwargs():
    request_id = 167
    uri = "io.xconn.new"
    args = ["args"]
    kwargs = {"new": "value"}
    message = messages.Call(messages.CallFields(request_id, uri, args, kwargs)).marshal()

    assert isinstance(message, list)
    assert len(message) == 6

    assert isinstance(message[0], int)
    assert message[0] == messages.Call.TYPE

    assert isinstance(message[1], int)
    assert message[1] == request_id

    assert message[2] == {}
    assert message[3] == uri

    assert isinstance(message[4], list)
    assert message[4] == args

    assert isinstance(message[5], dict)
    assert message[5] == kwargs


def test_marshal_with_all_options():
    request_id = 1677
    uri = "io.xconn.ping"
    args = ["arg1"]
    kwargs = {"key": "value"}
    options = {"receive_progress": True}
    message = messages.Call(messages.CallFields(request_id, uri, args, kwargs, options)).marshal()

    assert isinstance(message, list)
    assert len(message) == 6

    assert isinstance(message[0], int)
    assert message[0] == messages.Call.TYPE

    assert isinstance(message[1], int)
    assert message[1] == request_id

    assert isinstance(message[2], dict)
    assert message[2] == options
    assert message[3] == uri

    assert isinstance(message[4], list)
    assert message[4] == args

    assert isinstance(message[5], dict)
    assert message[5] == kwargs
