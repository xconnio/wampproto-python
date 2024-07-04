import pytest

from tests.interoptests.helpers import run_command
from wampproto import messages
from wampproto.serializers import JSONSerializer, CBORSerializer, MsgPackSerializer


def is_equal(msg1: messages.Hello, msg2: messages.Hello) -> bool:
    return (
        msg1.realm == msg2.realm
        and msg1.roles == msg2.roles
        and msg1.authid == msg2.authid
        and msg1.authmethods == msg2.authmethods
        and msg1.authextra == msg2.authextra
    )


@pytest.mark.asyncio
async def test_json_serializer():
    msg = messages.Hello(
        messages.HelloFields(
            "realm1", roles={"callee": True}, authid="foo", authmethods=["anonymous"], authextra={"foo": "bar"}
        )
    )
    command = (
        f"wampproto message hello {msg.realm} anonymous --authid {msg.authid} -e foo=bar "
        f"-r callee=true --serializer json"
    )

    output = await run_command(command)

    serializer = JSONSerializer()
    message = serializer.deserialize(output)

    assert is_equal(msg, message)


@pytest.mark.asyncio
async def test_cbor_serializer():
    msg = messages.Hello(
        messages.HelloFields("realm1", roles={"callee": True}, authid="foo", authmethods=["anonymous"], authextra={})
    )
    command = (
        f"wampproto message hello {msg.realm} anonymous --authid {msg.authid} -r callee=true --output hex"
        f" --serializer cbor"
    )

    output = await run_command(command)
    output_bytes = bytes.fromhex(output)

    serializer = CBORSerializer()
    message = serializer.deserialize(output_bytes)

    assert is_equal(msg, message)


@pytest.mark.asyncio
async def test_msgpack_serializer():
    msg = messages.Hello(
        messages.HelloFields(
            "realm1", roles={"callee": True}, authid="foo", authmethods=["anonymous"], authextra={"foo": "bar"}
        )
    )
    command = (
        f"wampproto message hello {msg.realm} anonymous --authid {msg.authid} -e foo=bar -r callee=true "
        f"--output hex --serializer msgpack"
    )

    output = await run_command(command)
    output_bytes = bytes.fromhex(output)

    serializer = MsgPackSerializer()
    message = serializer.deserialize(output_bytes)

    assert is_equal(msg, message)
