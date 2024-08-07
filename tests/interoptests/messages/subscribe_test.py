import pytest

from tests.interoptests.helpers import run_command
from wampproto import messages
from wampproto.serializers import JSONSerializer, CBORSerializer, MsgPackSerializer

TEST_TOPIC = "io.xconn.test"


def is_equal(msg1: messages.Subscribe, msg2: messages.Subscribe) -> bool:
    return msg1.request_id == msg2.request_id and msg1.topic == msg2.topic and msg1.options == msg2.options


@pytest.mark.asyncio
async def test_json_serializer():
    msg = messages.Subscribe(messages.SubscribeFields(1, TEST_TOPIC))
    command = f"wampproto message subscribe {msg.request_id} {msg.topic} --serializer json"

    output = await run_command(command)

    serializer = JSONSerializer()
    message = serializer.deserialize(output)

    assert is_equal(msg, message)


@pytest.mark.asyncio
async def test_cbor_serializer():
    msg = messages.Subscribe(messages.SubscribeFields(1, TEST_TOPIC))
    command = f"wampproto message subscribe {msg.request_id} {msg.topic} --serializer cbor --output hex"

    output = await run_command(command)
    output_bytes = bytes.fromhex(output)

    serializer = CBORSerializer()
    message = serializer.deserialize(output_bytes)

    assert is_equal(msg, message)


@pytest.mark.asyncio
async def test_msgpack_serializer():
    msg = messages.Subscribe(messages.SubscribeFields(1, TEST_TOPIC))
    command = f"wampproto message subscribe {msg.request_id} {msg.topic} --serializer msgpack --output hex"

    output = await run_command(command)
    output_bytes = bytes.fromhex(output)

    serializer = MsgPackSerializer()
    message = serializer.deserialize(output_bytes)

    assert is_equal(msg, message)


@pytest.mark.asyncio
async def test_with_options():
    msg = messages.Subscribe(messages.SubscribeFields(1, TEST_TOPIC, options={"a": "b"}))
    command = f"wampproto message subscribe {msg.request_id} {msg.topic} -o a=b --serializer json"

    output = await run_command(command)

    serializer = JSONSerializer()
    message = serializer.deserialize(output)

    assert is_equal(msg, message)
