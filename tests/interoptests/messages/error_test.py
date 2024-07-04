import pytest

from tests.interoptests.helpers import run_command
from wampproto import messages
from wampproto.serializers import JSONSerializer, CBORSerializer, MsgPackSerializer


def is_equal(msg1: messages.Error, msg2: messages.Error) -> bool:
    return (
        msg1.message_type == msg2.message_type
        and msg1.request_id == msg2.request_id
        and msg1.uri == msg2.uri
        and msg1.details == msg2.details
        and msg1.args == msg2.args
        and msg1.kwargs == msg2.kwargs
    )


@pytest.mark.asyncio
async def test_json_serializer():
    msg = messages.Error(messages.ErrorFields(1, 1, "wamp.error"))
    command = f"wampproto message error {msg.message_type} {msg.request_id} {msg.uri} --serializer json"

    output = await run_command(command)

    serializer = JSONSerializer()
    message = serializer.deserialize(output)

    assert is_equal(msg, message)


@pytest.mark.asyncio
async def test_cbor_serializer():
    msg = messages.Error(messages.ErrorFields(1, 1, "wamp.error"))
    command = f"wampproto message error {msg.message_type} {msg.request_id} {msg.uri} --serializer cbor --output hex"

    output = await run_command(command)
    output_bytes = bytes.fromhex(output)

    serializer = CBORSerializer()
    message = serializer.deserialize(output_bytes)

    assert is_equal(msg, message)


@pytest.mark.asyncio
async def test_msgpack_serializer():
    msg = messages.Error(messages.ErrorFields(1, 1, "wamp.error"))
    command = f"wampproto message error {msg.message_type} {msg.request_id} {msg.uri} --serializer msgpack --output hex"

    output = await run_command(command)
    output_bytes = bytes.fromhex(output)

    serializer = MsgPackSerializer()
    message = serializer.deserialize(output_bytes)

    assert is_equal(msg, message)


@pytest.mark.asyncio
async def test_with_args_kwargs_details():
    msg = messages.Error(messages.ErrorFields(1, 1, "wamp.error", details={"a": "b"}, args=["foo"], kwargs={"a": "b"}))
    command = (
        f"wampproto message error {msg.message_type} {msg.request_id} {msg.uri} foo -d a=b -k a=b --serializer json"
    )

    output = await run_command(command)

    serializer = JSONSerializer()
    message = serializer.deserialize(output)

    assert is_equal(msg, message)
