from wampproto.messages import Hello
from wampproto.serializers.msgpack import MsgPackSerializer


def test_serializer():
    serializer = MsgPackSerializer()
    hello = Hello.parse([1, "realm1", {"roles": {"callee": {}}}])

    data = serializer.serialize(hello)
    assert isinstance(data, bytes)

    obj = serializer.deserialize(data)
    assert isinstance(obj, Hello)
    assert obj.realm == hello.realm
    assert obj.roles == hello.roles
