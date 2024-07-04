import pytest

from tests.interoptests.helpers import run_command
from wampproto import messages
from wampproto.serializers import JSONSerializer, CBORSerializer, MsgPackSerializer


def is_equal(msg1: messages.Event, msg2: messages.Event) -> bool:
    return (
        msg1.subscription_id == msg2.subscription_id
        and msg1.publication_id == msg2.publication_id
        and msg1.details == msg2.details
        and msg1.args == msg2.args
        and msg1.kwargs == msg2.kwargs
    )


@pytest.mark.asyncio
async def test_json_serializer():
    msg = messages.Event(messages.EventFields(1, 1))
    command = f"wampproto message event {msg.subscription_id} {msg.publication_id} --serializer json"

    output = await run_command(command)

    serializer = JSONSerializer()
    message = serializer.deserialize(output)

    assert is_equal(msg, message)


@pytest.mark.asyncio
async def test_cbor_serializer():
    msg = messages.Event(messages.EventFields(1, 1))
    command = f"wampproto message event {msg.subscription_id} {msg.publication_id} --serializer cbor --output hex"

    output = await run_command(command)
    output_bytes = bytes.fromhex(output)

    serializer = CBORSerializer()
    message = serializer.deserialize(output_bytes)

    assert is_equal(msg, message)


@pytest.mark.asyncio
async def test_msgpack_serializer():
    msg = messages.Event(messages.EventFields(1, 1))
    command = f"wampproto message event {msg.subscription_id} {msg.publication_id} --serializer msgpack --output hex"

    output = await run_command(command)
    output_bytes = bytes.fromhex(output)

    serializer = MsgPackSerializer()
    message = serializer.deserialize(output_bytes)

    assert is_equal(msg, message)


@pytest.mark.asyncio
async def test_with_args_kwargs_details():
    msg = messages.Event(messages.EventFields(1, 1, details={"a": "b"}, args=["abc", 123], kwargs={"a": "b"}))
    command = (
        f"wampproto message event {msg.subscription_id} {msg.publication_id} abc 123 -d a=b -k a=b --serializer json"
    )

    output = await run_command(command)

    serializer = JSONSerializer()
    message = serializer.deserialize(output)

    assert is_equal(msg, message)
