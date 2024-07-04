import pytest

from tests.interoptests.helpers import run_command
from wampproto import messages
from wampproto.serializers import JSONSerializer, CBORSerializer, MsgPackSerializer


def is_equal(msg1: messages.Authenticate, msg2: messages.Authenticate) -> bool:
    return msg1.signature == msg2.signature and msg1.extra == msg2.extra


@pytest.mark.asyncio
async def test_json_serializer():
    msg = messages.Authenticate(messages.AuthenticateFields("signature", extra={"ticket": "test"}))
    command = f"wampproto message authenticate {msg.signature} -e ticket=test --serializer json"

    output = await run_command(command)

    serializer = JSONSerializer()
    message = serializer.deserialize(output)

    assert is_equal(msg, message)


@pytest.mark.asyncio
async def test_cbor_serializer():
    msg = messages.Authenticate(messages.AuthenticateFields("signature"))
    command = f"wampproto message authenticate {msg.signature} --serializer cbor --output hex"

    output = await run_command(command)
    output_bytes = bytes.fromhex(output)

    serializer = CBORSerializer()
    message = serializer.deserialize(output_bytes)

    assert is_equal(msg, message)


@pytest.mark.asyncio
async def test_msgpack_serializer():
    msg = messages.Authenticate(messages.AuthenticateFields("signature", extra={"secret": "test"}))
    command = f"wampproto message authenticate {msg.signature} -e secret=test --serializer msgpack --output hex"

    output = await run_command(command)
    output_bytes = bytes.fromhex(output)

    serializer = MsgPackSerializer()
    message = serializer.deserialize(output_bytes)

    assert is_equal(msg, message)
