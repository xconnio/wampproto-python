import pytest

from tests.interoptests.helpers import run_command
from wampproto import messages
from wampproto.serializers import JSONSerializer, CBORSerializer, MsgPackSerializer

TEST_PROCEDURE = "io.xconn.test"


def is_equal(msg1: messages.Call, msg2: messages.Call) -> bool:
    return (
        msg1.request_id == msg2.request_id
        and msg1.uri == msg2.uri
        and msg1.options == msg2.options
        and msg1.args == msg2.args
        and msg1.kwargs == msg2.kwargs
    )


@pytest.mark.asyncio
async def test_json_serializer():
    call_message = messages.Call(messages.CallFields(1, TEST_PROCEDURE))
    command = f"wampproto message call {call_message.request_id} {call_message.uri} --serializer json"

    output = await run_command(command)

    serializer = JSONSerializer()
    message = serializer.deserialize(output)

    assert is_equal(call_message, message)


@pytest.mark.asyncio
async def test_cbor_serializer():
    call_message = messages.Call(messages.CallFields(1, TEST_PROCEDURE))
    command = f"wampproto message call {call_message.request_id} {call_message.uri} --serializer cbor --output hex"

    output = await run_command(command)
    output_bytes = bytes.fromhex(output)

    serializer = CBORSerializer()
    message = serializer.deserialize(output_bytes)

    assert is_equal(call_message, message)


@pytest.mark.asyncio
async def test_msgpack_serializer():
    call_message = messages.Call(messages.CallFields(1, TEST_PROCEDURE))
    command = f"wampproto message call {call_message.request_id} {call_message.uri} --serializer msgpack --output hex"

    output = await run_command(command)
    output_bytes = bytes.fromhex(output)

    serializer = MsgPackSerializer()
    message = serializer.deserialize(output_bytes)

    assert is_equal(call_message, message)


@pytest.mark.asyncio
async def test_with_args_kwargs():
    call_message = messages.Call(messages.CallFields(1, TEST_PROCEDURE, args=["abc", 123], kwargs={"a": "b"}))
    command = f"wampproto message call {call_message.request_id} {call_message.uri} abc 123 -k a=b --serializer json"

    output = await run_command(command)

    serializer = JSONSerializer()
    message = serializer.deserialize(output)

    assert is_equal(call_message, message)
