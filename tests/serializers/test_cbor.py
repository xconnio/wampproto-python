from wampproto.messages.hello import Hello
from wampproto.serializers.cbor import CBORSerializer


def test_serializer():
    serializer = CBORSerializer()
    hello = Hello.parse([1, "realm1", {"roles": {"caller": {}}}])

    data = serializer.serialize(hello)
    assert isinstance(data, bytes)

    obj = serializer.deserialize(data)
    assert isinstance(obj, Hello)
    assert obj.realm == hello.realm
    assert obj.roles == hello.roles
