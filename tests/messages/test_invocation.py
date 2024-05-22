import pytest

from wampproto import messages
from wampproto.messages import util


def test_parse_with_invalid_type():
    message = "new message"
    with pytest.raises(ValueError) as exc_info:
        messages.Invocation.parse(message)

    assert str(exc_info.value) == f"invalid message type str for {messages.Invocation.TEXT}, type should be a list"


def test_parse_with_invalid_list_min_length():
    message = ["bar"]
    with pytest.raises(ValueError) as exc_info:
        messages.Invocation.parse(message)

    assert str(exc_info.value) == "invalid message length 1, must be at least 4"


def test_parse_with_invalid_list_max_length():
    message = ["bar", 1, 3, 443, 23, 432, 2]
    with pytest.raises(ValueError) as exc_info:
        messages.Invocation.parse(message)

    assert str(exc_info.value) == "invalid message length 7, must be at most 6"


def test_parse_with_invalid_message_type():
    msg_type = 9
    message = [msg_type, 123, 456, {}]
    with pytest.raises(ValueError) as exc_info:
        messages.Invocation.parse(message)

    assert (
        str(exc_info.value) == f"invalid message id 9 for {messages.Invocation.TEXT}, "
        f"expected {messages.Invocation.TYPE}"
    )


def test_parse_with_negative_request_id():
    message = [messages.Invocation.TYPE, -1, 365, {}]
    with pytest.raises(ValueError) as exc_info:
        messages.Invocation.parse(message)

    assert (
        str(exc_info.value)
        == f"{messages.Invocation.TEXT}: value at index 1 must be between '{util.MIN_ID}' and '{util.MAX_ID}' "
           f"but was -1"
    )


def test_parse_with_out_of_range_request_value():
    value = 9007199254740993
    message = [messages.Invocation.TYPE, value, 23, {}]
    with pytest.raises(ValueError) as exc_info:
        messages.Invocation.parse(message)

    assert (
        str(exc_info.value)
        == f"{messages.Invocation.TEXT}: value at index 1 must be between '{util.MIN_ID}' and '{util.MAX_ID}' "
           f"but was {value}"
    )


def test_parse_with_negative_registration_id():
    message = [messages.Invocation.TYPE, 17, -39, {}]
    with pytest.raises(ValueError) as exc_info:
        messages.Invocation.parse(message)

    assert (
        str(exc_info.value)
        == f"{messages.Invocation.TEXT}: value at index 2 must be between '{util.MIN_ID}' and '{util.MAX_ID}' "
           f"but was -39"
    )


def test_parse_with_out_of_range_registration_value():
    value = 9007199254740993
    message = [messages.Invocation.TYPE, 80, value, {}]
    with pytest.raises(ValueError) as exc_info:
        messages.Invocation.parse(message)

    assert (
        str(exc_info.value)
        == f"{messages.Invocation.TEXT}: value at index 2 must be between '{util.MIN_ID}' and '{util.MAX_ID}' "
           f"but was {value}"
    )


def test_parse_with_invalid_options_type():
    message = [messages.Invocation.TYPE, 80, 753, ["options"]]
    with pytest.raises(ValueError) as exc_info:
        messages.Invocation.parse(message)

    assert (
        str(exc_info.value)
        == f"{messages.Invocation.TEXT}: value at index 3 must be of type '{util.DICT}' but was list"
    )


def test_parse_with_invalid_args_type():
    message = [messages.Invocation.TYPE, 370, 98, {}, "args"]
    with pytest.raises(ValueError) as exc_info:
        messages.Invocation.parse(message)

    assert (
        str(exc_info.value) == f"{messages.Invocation.TEXT}: value at index 4 must be of type '{util.LIST}' but was str"
    )


def test_parse_with_invalid_kwargs_type():
    message = [messages.Invocation.TYPE, 67, 147, {}, [], ["kwargs"]]
    with pytest.raises(ValueError) as exc_info:
        messages.Invocation.parse(message)

    assert (
        str(exc_info.value)
        == f"{messages.Invocation.TEXT}: value at index 5 must be of type '{util.DICT}' but was list"
    )


def test_parse_correctly():
    request_id = 74
    registration_id = 14
    message = [messages.Invocation.TYPE, request_id, registration_id, {}]
    invocation = messages.Invocation.parse(message)

    assert isinstance(invocation, messages.Invocation)

    assert isinstance(invocation.request_id, int)
    assert invocation.request_id == request_id

    assert isinstance(invocation.registration_id, int)
    assert invocation.registration_id == registration_id

    assert invocation.args is None
    assert invocation.kwargs is None
    assert invocation.details == {}


def test_parse_correctly_with_options():
    request_id = 741
    registration_id = 142
    details = {"extra": True}
    message = [messages.Invocation.TYPE, request_id, registration_id, details]
    invocation = messages.Invocation.parse(message)

    assert isinstance(invocation, messages.Invocation)

    assert isinstance(invocation.request_id, int)
    assert invocation.request_id == request_id

    assert isinstance(invocation.registration_id, int)
    assert invocation.registration_id == registration_id

    assert invocation.details == details
    assert invocation.args is None
    assert invocation.kwargs is None


def test_parse_correctly_with_args():
    request_id = 741
    registration_id = 142
    args = [1, 2]
    message = [messages.Invocation.TYPE, request_id, registration_id, {}, args]
    invocation = messages.Invocation.parse(message)

    assert isinstance(invocation, messages.Invocation)

    assert isinstance(invocation.request_id, int)
    assert invocation.request_id == request_id

    assert isinstance(invocation.registration_id, int)
    assert invocation.registration_id == registration_id

    assert isinstance(invocation.args, list)
    assert invocation.args == args

    assert invocation.kwargs is None
    assert invocation.details == {}


def test_parse_correctly_with_kwargs():
    request_id = 73
    registration_id = 12
    kwargs = {"fruit": "grape"}
    message = [messages.Invocation.TYPE, request_id, registration_id, {}, [], kwargs]
    invocation = messages.Invocation.parse(message)

    assert isinstance(invocation, messages.Invocation)

    assert isinstance(invocation.request_id, int)
    assert invocation.request_id == request_id

    assert isinstance(invocation.registration_id, int)
    assert invocation.registration_id == registration_id

    assert isinstance(invocation.kwargs, dict)
    assert invocation.kwargs == kwargs

    assert invocation.args == []
    assert invocation.details == {}


def test_parse_correctly_with_all_options():
    request_id = 673
    registration_id = 152
    args = ["1st"]
    kwargs = {"fruit": "apple"}
    details = {"caller_authrole": "user"}
    message = [messages.Invocation.TYPE, request_id, registration_id, details, args, kwargs]
    invocation = messages.Invocation.parse(message)

    assert isinstance(invocation, messages.Invocation)

    assert isinstance(invocation.request_id, int)
    assert invocation.request_id == request_id

    assert isinstance(invocation.registration_id, int)
    assert invocation.registration_id == registration_id

    assert isinstance(invocation.args, list)
    assert invocation.args == args

    assert isinstance(invocation.kwargs, dict)
    assert invocation.kwargs == kwargs

    assert isinstance(invocation.details, dict)
    assert invocation.details == details


def test_marshal():
    request_id = 612723
    registration_id = 171952
    message = messages.Invocation(request_id, registration_id).marshal()

    assert isinstance(message, list)
    assert len(message) == 4

    assert isinstance(message[0], int)
    assert message[0] == messages.Invocation.TYPE

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
    assert message[0] == messages.Invocation.TYPE

    assert isinstance(message[1], int)
    assert message[1] == request_id

    assert isinstance(message[2], int)
    assert message[2] == registration_id

    assert message[3] == {}

    assert isinstance(message[4], list)
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
    assert message[0] == messages.Invocation.TYPE

    assert isinstance(message[1], int)
    assert message[1] == request_id

    assert isinstance(message[2], int)
    assert message[2] == registration_id

    assert message[3] == {}

    assert isinstance(message[4], list)
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
    assert message[0] == messages.Invocation.TYPE

    assert isinstance(message[1], int)
    assert message[1] == request_id

    assert isinstance(message[2], int)
    assert message[2] == registration_id

    assert isinstance(message[3], dict)
    assert message[3] == details

    assert isinstance(message[4], list)
    assert message[4] == args

    assert isinstance(message[5], dict)
    assert message[5] == kwargs
