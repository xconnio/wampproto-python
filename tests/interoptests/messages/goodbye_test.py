import pytest

from tests.interoptests.helpers import run_command
from wampproto import messages
from wampproto.serializers import JSONSerializer, CBORSerializer, MsgPackSerializer


def is_equal(msg1: messages.Goodbye, msg2: messages.Goodbye) -> bool:
    return msg1.reason == msg2.reason and msg1.details == msg2.details


@pytest.mark.asyncio
async def test_json_serializer():
    msg = messages.Goodbye(messages.GoodbyeFields(details={}, reason="crash"))
    command = f"wampproto message goodbye {msg.reason} --serializer json"

    output = await run_command(command)

    serializer = JSONSerializer()
    message = serializer.deserialize(output)

    assert is_equal(msg, message)


@pytest.mark.asyncio
async def test_cbor_serializer():
    msg = messages.Goodbye(messages.GoodbyeFields(details={}, reason="crash"))
    command = f"wampproto message goodbye {msg.reason} --serializer cbor --output hex"

    output = await run_command(command)
    output_bytes = bytes.fromhex(output)

    serializer = CBORSerializer()
    message = serializer.deserialize(output_bytes)

    assert is_equal(msg, message)


@pytest.mark.asyncio
async def test_msgpack_serializer():
    msg = messages.Goodbye(messages.GoodbyeFields(details={}, reason="crash"))
    command = f"wampproto message goodbye {msg.reason} --serializer msgpack --output hex"

    output = await run_command(command)
    output_bytes = bytes.fromhex(output)

    serializer = MsgPackSerializer()
    message = serializer.deserialize(output_bytes)

    assert is_equal(msg, message)


@pytest.mark.asyncio
async def test_with_details():
    msg = messages.Goodbye(messages.GoodbyeFields(details={"a": "b"}, reason="crash"))
    command = f"wampproto message goodbye {msg.reason} -d a=b --serializer json"

    output = await run_command(command)

    serializer = JSONSerializer()
    message = serializer.deserialize(output)

    assert is_equal(msg, message)
