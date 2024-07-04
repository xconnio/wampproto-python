import pytest

from tests.interoptests.helpers import run_command
from wampproto import messages
from wampproto.serializers import JSONSerializer, CBORSerializer, MsgPackSerializer


def is_equal(msg1: messages.Interrupt, msg2: messages.Interrupt) -> bool:
    return msg1.request_id == msg2.request_id and msg1.options == msg2.options


@pytest.mark.asyncio
async def test_json_serializer():
    msg = messages.Interrupt(messages.InterruptFields(1))
    command = f"wampproto message interrupt {msg.request_id} --serializer json"

    output = await run_command(command)

    serializer = JSONSerializer()
    message = serializer.deserialize(output)

    assert is_equal(msg, message)


@pytest.mark.asyncio
async def test_cbor_serializer():
    msg = messages.Interrupt(messages.InterruptFields(1))
    command = f"wampproto message interrupt {msg.request_id} --serializer cbor --output hex"

    output = await run_command(command)
    output_bytes = bytes.fromhex(output)

    serializer = CBORSerializer()
    message = serializer.deserialize(output_bytes)

    assert is_equal(msg, message)


@pytest.mark.asyncio
async def test_msgpack_serializer():
    msg = messages.Interrupt(messages.InterruptFields(1))
    command = f"wampproto message interrupt {msg.request_id} --serializer msgpack --output hex"

    output = await run_command(command)
    output_bytes = bytes.fromhex(output)

    serializer = MsgPackSerializer()
    message = serializer.deserialize(output_bytes)

    assert is_equal(msg, message)


@pytest.mark.asyncio
async def test_with_options():
    msg = messages.Interrupt(messages.InterruptFields(1, options={"a": "b"}))
    command = f"wampproto message interrupt {msg.request_id} -o a=b --serializer json"

    output = await run_command(command)

    serializer = JSONSerializer()
    message = serializer.deserialize(output)

    assert is_equal(msg, message)
