import pytest

from tests.interoptests.helpers import run_command
from wampproto import messages
from wampproto.serializers import JSONSerializer, CBORSerializer, MsgPackSerializer

TEST_TOPIC = "io.xconn.test"


def is_equal(msg1: messages.Publish, msg2: messages.Publish) -> bool:
    return (
        msg1.request_id == msg2.request_id
        and msg1.uri == msg2.uri
        and msg1.options == msg2.options
        and msg1.args == msg2.args
        and msg1.kwargs == msg2.kwargs
    )


@pytest.mark.asyncio
async def test_json_serializer():
    msg = messages.Publish(messages.PublishFields(1, TEST_TOPIC))
    command = f"wampproto message publish {msg.request_id} {msg.uri} --serializer json"

    output = await run_command(command)

    serializer = JSONSerializer()
    message = serializer.deserialize(output)

    assert is_equal(msg, message)


@pytest.mark.asyncio
async def test_cbor_serializer():
    msg = messages.Publish(messages.PublishFields(1, TEST_TOPIC))
    command = f"wampproto message publish {msg.request_id} {msg.uri} --serializer cbor --output hex"

    output = await run_command(command)
    output_bytes = bytes.fromhex(output)

    serializer = CBORSerializer()
    message = serializer.deserialize(output_bytes)

    assert is_equal(msg, message)


@pytest.mark.asyncio
async def test_msgpack_serializer():
    msg = messages.Publish(messages.PublishFields(1, TEST_TOPIC))
    command = f"wampproto message publish {msg.request_id} {msg.uri} --serializer msgpack --output hex"

    output = await run_command(command)
    output_bytes = bytes.fromhex(output)

    serializer = MsgPackSerializer()
    message = serializer.deserialize(output_bytes)

    assert is_equal(msg, message)


@pytest.mark.asyncio
async def test_with_args_kwargs_options():
    msg = messages.Publish(
        messages.PublishFields(1, TEST_TOPIC, options={"a": "b"}, args=["abc", 123], kwargs={"a": "b"})
    )
    command = f"wampproto message publish {msg.request_id} {msg.uri} abc 123 -o a=b -k a=b --serializer json"

    output = await run_command(command)

    serializer = JSONSerializer()
    message = serializer.deserialize(output)

    assert is_equal(msg, message)
