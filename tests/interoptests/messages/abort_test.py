import pytest

from tests.interoptests.helpers import run_command
from wampproto import messages
from wampproto.serializers import JSONSerializer, CBORSerializer, MsgPackSerializer


def is_equal(msg1: messages.Abort, msg2: messages.Abort) -> bool:
    return (
        msg1.reason == msg2.reason
        and msg1.details == msg2.details
        and msg1.args == msg2.args
        and msg1.kwargs == msg2.kwargs
    )


@pytest.mark.asyncio
async def test_json_serializer():
    msg = messages.Abort(messages.AbortFields(details={}, reason="crash"))
    command = f"wampproto message abort {msg.reason} --serializer json"

    output = await run_command(command)

    serializer = JSONSerializer()
    message = serializer.deserialize(output)

    assert is_equal(msg, message)


@pytest.mark.asyncio
async def test_cbor_serializer():
    msg = messages.Abort(messages.AbortFields(details={}, reason="crash"))
    command = f"wampproto message abort {msg.reason} --serializer cbor --output hex"

    output = await run_command(command)
    output_bytes = bytes.fromhex(output)

    serializer = CBORSerializer()
    message = serializer.deserialize(output_bytes)

    assert is_equal(msg, message)


@pytest.mark.asyncio
async def test_msgpack_serializer():
    msg = messages.Abort(messages.AbortFields(details={}, reason="crash"))
    command = f"wampproto message abort {msg.reason} --serializer msgpack --output hex"

    output = await run_command(command)
    output_bytes = bytes.fromhex(output)

    serializer = MsgPackSerializer()
    message = serializer.deserialize(output_bytes)

    assert is_equal(msg, message)


@pytest.mark.asyncio
async def test_with_args_kwargs_details():
    msg = messages.Abort(messages.AbortFields(details={"a": "b"}, reason="crash", args=["foo"], kwargs={"a": "b"}))
    command = f"wampproto message abort {msg.reason} foo -d a=b -k a=b --serializer json"

    output = await run_command(command)

    serializer = JSONSerializer()
    message = serializer.deserialize(output)

    assert is_equal(msg, message)
