import pytest

from wamp import messages
from wamp.messages import error


def test_parse_with_invalid_type():
    message = "new message"
    with pytest.raises(error.InvalidTypeError) as exc_info:
        messages.Invocation.parse(message)

    assert (
        str(exc_info.value)
        == f"invalid type: expected type 'list', got 'str' for message in '{messages.Call.Call_TEXT}'"
    )


def test_parse_with_invalid_list_length():
    message = ["bar"]
    with pytest.raises(error.InvalidMessageLengthError) as exc_info:
        messages.Invocation.parse(message)

    assert (
        str(exc_info.value)
        == f"invalid message length: expected length 'between 4 & 6', got '1' for '{messages.Call.Call_TEXT}'"
    )


def test_parse_with_invalid_message_type():
    msg_type = 9
    message = [msg_type, 123, 456, {}]
    with pytest.raises(error.InvalidMessageTypeError) as exc_info:
        messages.Invocation.parse(message)

    assert (
        str(exc_info.value) == f"invalid message type: "
        f"message type for {messages.Invocation.INVOCATION_TEXT} is '{messages.Invocation.MESSAGE_TYPE}', got '{msg_type}'"
    )


def test_parse_with_negative_request_id():
    message = [messages.Invocation.MESSAGE_TYPE, -1, 365, {}]
    with pytest.raises(error.ProtocolError) as exc_info:
        messages.Invocation.parse(message)

    assert str(exc_info.value) == f"invalid request ID value for {messages.Invocation.INVOCATION_TEXT}"


def test_parse_with_out_of_range_request_value():
    message = [messages.Invocation.MESSAGE_TYPE, 9007199254740993, 23, {}]
    with pytest.raises(error.ProtocolError) as exc_info:
        messages.Invocation.parse(message)

    assert str(exc_info.value) == f"invalid request ID value for {messages.Invocation.INVOCATION_TEXT}"


def test_parse_with_negative_registration_id():
    message = [messages.Invocation.MESSAGE_TYPE, 17, -39, {}]
    with pytest.raises(error.ProtocolError) as exc_info:
        messages.Invocation.parse(message)

    assert str(exc_info.value) == f"invalid registration ID value for {messages.Invocation.INVOCATION_TEXT}"


def test_parse_with_out_of_range_registration_value():
    message = [messages.Invocation.MESSAGE_TYPE, 80, 9007199254740993, {}]
    with pytest.raises(error.ProtocolError) as exc_info:
        messages.Invocation.parse(message)

    assert str(exc_info.value) == f"invalid registration ID value for {messages.Invocation.INVOCATION_TEXT}"


def test_parse_with_invalid_options_type():
    message = [messages.Invocation.MESSAGE_TYPE, 80, 753, ["options"]]
    with pytest.raises(error.InvalidDetailsError) as exc_info:
        messages.Invocation.parse(message)

    assert str(exc_info.value) == f"options must be of type dictionary for {messages.Call.Call_TEXT}"


def test_parse_with_invalid_options_dict_key():
    message = [messages.Invocation.MESSAGE_TYPE, 80, 753, {98: "test"}]
    with pytest.raises(error.InvalidDetailsError) as exc_info:
        messages.Invocation.parse(message)

    assert str(exc_info.value) == f"invalid type for key '98' in extra details for {messages.Call.Call_TEXT}"


def test_parse_with_invalid_args_type():
    message = [messages.Invocation.MESSAGE_TYPE, 370, 98, {}, "args"]
    with pytest.raises(error.InvalidTypeError) as exc_info:
        messages.Invocation.parse(message)

    assert (
        str(exc_info.value)
        == f"invalid type: expected type 'list', got 'str' for args in '{messages.Invocation.INVOCATION_TEXT}'"
    )


def test_parse_with_invalid_kwargs_type():
    message = [messages.Invocation.MESSAGE_TYPE, 67, 147, {}, [], ["kwargs"]]
    with pytest.raises(error.InvalidTypeError) as exc_info:
        messages.Invocation.parse(message)

    assert (
        str(exc_info.value)
        == f"invalid type: expected type 'dict', got 'list' for kwargs in '{messages.Invocation.INVOCATION_TEXT}'"
    )


def test_parse_correctly():
    request_id = 74
    registration_id = 14
    message = [messages.Invocation.MESSAGE_TYPE, request_id, registration_id, {}]
    call = messages.Invocation.parse(message)

    assert isinstance(call, messages.Invocation)

    assert isinstance(call.request_id, int)
    assert call.request_id == request_id

    assert isinstance(call.registration_id, int)
    assert call.registration_id == registration_id

    assert call.args is None
    assert call.kwargs is None
    assert call.details == {}


def test_parse_correctly_with_options():
    request_id = 741
    registration_id = 142
    details = {"extra": True}
    message = [messages.Invocation.MESSAGE_TYPE, request_id, registration_id, details]
    call = messages.Invocation.parse(message)

    assert isinstance(call, messages.Invocation)

    assert isinstance(call.request_id, int)
    assert call.request_id == request_id

    assert isinstance(call.registration_id, int)
    assert call.registration_id == registration_id

    assert call.details == details
    assert call.args is None
    assert call.kwargs is None


def test_parse_correctly_with_args():
    request_id = 741
    registration_id = 142
    args = [1, 2]
    message = [messages.Invocation.MESSAGE_TYPE, request_id, registration_id, {}, args]
    call = messages.Invocation.parse(message)

    assert isinstance(call, messages.Invocation)

    assert isinstance(call.request_id, int)
    assert call.request_id == request_id

    assert isinstance(call.registration_id, int)
    assert call.registration_id == registration_id

    assert isinstance(call.args, list)
    assert call.args == args

    assert call.kwargs is None
    assert call.details == {}


def test_parse_correctly_with_kwargs():
    request_id = 73
    registration_id = 12
    kwargs = {"fruit": "grape"}
    message = [messages.Invocation.MESSAGE_TYPE, request_id, registration_id, {}, [], kwargs]
    call = messages.Invocation.parse(message)

    assert isinstance(call, messages.Invocation)

    assert isinstance(call.request_id, int)
    assert call.request_id == request_id

    assert isinstance(call.registration_id, int)
    assert call.registration_id == registration_id

    assert isinstance(call.kwargs, dict)
    assert call.kwargs == kwargs

    assert call.args == []
    assert call.details == {}


def test_parse_correctly_with_all_options():
    request_id = 673
    registration_id = 152
    args = ["1st"]
    kwargs = {"fruit": "apple"}
    details = {"caller_authrole": "user"}
    message = [messages.Invocation.MESSAGE_TYPE, request_id, registration_id, details, args, kwargs]
    call = messages.Invocation.parse(message)

    assert isinstance(call, messages.Invocation)

    assert isinstance(call.request_id, int)
    assert call.request_id == request_id

    assert isinstance(call.registration_id, int)
    assert call.registration_id == registration_id

    assert isinstance(call.args, list)
    assert call.args == args

    assert isinstance(call.kwargs, dict)
    assert call.kwargs == kwargs

    assert isinstance(call.details, dict)
    assert call.details == details


def test_marshal():
    request_id = 612723
    registration_id = 171952
    message = messages.Invocation(request_id, registration_id).marshal()

    assert isinstance(message, list)
    assert len(message) == 4

    assert isinstance(message[0], int)
    assert message[0] == messages.Invocation.MESSAGE_TYPE

    assert isinstance(message[1], int)
    assert message[1] == request_id

    assert isinstance(message[2], int)
    assert message[2] == registration_id

    assert message[3] == {}


def test_marshal_with_args():
    request_id = 61273
    registration_id = 17152
    args = ["2nd"]
    message = messages.Invocation(request_id, registration_id, args).marshal()

    assert isinstance(message, list)
    assert len(message) == 5

    assert isinstance(message[0], int)
    assert message[0] == messages.Invocation.MESSAGE_TYPE

    assert isinstance(message[1], int)
    assert message[1] == request_id

    assert isinstance(message[2], int)
    assert message[2] == registration_id

    assert message[3] == {}

    assert isinstance(args, list)
    assert message[4] == args


def test_marshal_with_kwargs():
    request_id = 6173
    registration_id = 1152
    args = ["2nd"]
    kwargs = {"fruit": "apple"}
    message = messages.Invocation(request_id, registration_id, args, kwargs).marshal()

    assert isinstance(message, list)
    assert len(message) == 6

    assert isinstance(message[0], int)
    assert message[0] == messages.Invocation.MESSAGE_TYPE

    assert isinstance(message[1], int)
    assert message[1] == request_id

    assert isinstance(message[2], int)
    assert message[2] == registration_id

    assert message[3] == {}

    assert isinstance(args, list)
    assert message[4] == args

    assert isinstance(message[5], dict)
    assert message[5] == kwargs


def test_marshal_with_all_options():
    request_id = 673
    registration_id = 152
    args = ["1st"]
    kwargs = {"fruit": "apple"}
    details = {"caller_authrole": "user"}
    message = messages.Invocation(request_id, registration_id, args, kwargs, details).marshal()

    assert isinstance(message, list)
    assert len(message) == 6

    assert isinstance(message[0], int)
    assert message[0] == messages.Invocation.MESSAGE_TYPE

    assert isinstance(message[1], int)
    assert message[1] == request_id

    assert isinstance(message[2], int)
    assert message[2] == registration_id

    assert isinstance(message[3], dict)
    assert message[3] == details

    assert isinstance(args, list)
    assert message[4] == args

    assert isinstance(message[5], dict)
    assert message[5] == kwargs