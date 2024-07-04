import pytest

from tests.interoptests.helpers import run_command
from wampproto import messages
from wampproto.serializers import JSONSerializer, CBORSerializer, MsgPackSerializer


def is_equal(msg1: messages.Published, msg2: messages.Published) -> bool:
    return msg1.request_id == msg2.request_id and msg1.publication_id == msg2.publication_id


@pytest.mark.asyncio
async def test_json_serializer():
    msg = messages.Published(messages.PublishedFields(1, 1))
    command = f"wampproto message published {msg.request_id} {msg.publication_id} --serializer json"

    output = await run_command(command)

    serializer = JSONSerializer()
    message = serializer.deserialize(output)

    assert is_equal(msg, message)


@pytest.mark.asyncio
async def test_cbor_serializer():
    msg = messages.Published(messages.PublishedFields(1, 1))
    command = f"wampproto message published {msg.request_id} {msg.publication_id} --serializer cbor --output hex"

    output = await run_command(command)
    output_bytes = bytes.fromhex(output)

    serializer = CBORSerializer()
    message = serializer.deserialize(output_bytes)

    assert is_equal(msg, message)


@pytest.mark.asyncio
async def test_msgpack_serializer():
    msg = messages.Published(messages.PublishedFields(1, 1))
    command = f"wampproto message published {msg.request_id} {msg.publication_id} --serializer msgpack --output hex"

    output = await run_command(command)
    output_bytes = bytes.fromhex(output)

    serializer = MsgPackSerializer()
    message = serializer.deserialize(output_bytes)

    assert is_equal(msg, message)
