import pytest

from tests.interoptests.helpers import run_command
from wampproto import messages
from wampproto.serializers import JSONSerializer, CBORSerializer, MsgPackSerializer


def is_equal(msg1: messages.Welcome, msg2: messages.Welcome) -> bool:
    return (
        msg1.session_id == msg2.session_id
        and msg1.roles == msg2.roles
        and msg1.authid == msg2.authid
        and msg1.authrole == msg2.authrole
        and msg1.authmethod == msg2.authmethod
        and msg1.authextra == msg2.authextra
    )


@pytest.mark.asyncio
async def test_json_serializer():
    msg = messages.Welcome(
        messages.WelcomeFields(
            1,
            roles={"callee": True},
            authid="foo",
            authrole="anonymous",
            authmethod="anonymous",
            authextra={"foo": 1},
        )
    )
    command = (
        f"wampproto message welcome {msg.session_id} --authmethod {msg.authmethod} --authid {msg.authid} "
        f"--roles callee=true --authextra foo=1 --authrole {msg.authrole} --serializer json"
    )

    output = await run_command(command)

    serializer = JSONSerializer()
    message = serializer.deserialize(output)

    assert is_equal(msg, message)


@pytest.mark.asyncio
async def test_cbor_serializer():
    msg = messages.Welcome(
        messages.WelcomeFields(
            1,
            roles={"callee": True},
            authid="foo",
            authrole="anonymous",
            authmethod="anonymous",
            authextra={},
        )
    )
    command = (
        f"wampproto message welcome {msg.session_id} --authmethod {msg.authmethod} --authid {msg.authid} "
        f"--roles callee=true --authrole {msg.authrole} --serializer cbor --output hex"
    )

    output = await run_command(command)
    output_bytes = bytes.fromhex(output)

    serializer = CBORSerializer()
    message = serializer.deserialize(output_bytes)

    assert is_equal(msg, message)


@pytest.mark.asyncio
async def test_msgpack_serializer():
    msg = messages.Welcome(
        messages.WelcomeFields(
            1,
            roles={"callee": True},
            authid="foo",
            authrole="anonymous",
            authmethod="anonymous",
            authextra={"foo": "bar"},
        )
    )
    command = (
        f"wampproto message welcome {msg.session_id} --authmethod {msg.authmethod} --authid {msg.authid} "
        f"--roles callee=true --authextra foo=bar --authrole {msg.authrole} --serializer msgpack --output hex"
    )

    output = await run_command(command)
    output_bytes = bytes.fromhex(output)

    serializer = MsgPackSerializer()
    message = serializer.deserialize(output_bytes)

    assert is_equal(msg, message)
