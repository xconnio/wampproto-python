from wampproto.messages.hello import Hello
from wampproto.serializers.json import JSONSerializer


def test_serializer():
    serializer = JSONSerializer()
    hello = Hello.parse([1, "realm1", {"roles": {"callee": {}}}])

    data = serializer.serialize(hello)
    assert isinstance(data, bytes)

    obj = serializer.deserialize(data)
    assert isinstance(obj, Hello)
    assert obj.realm == hello.realm
    assert obj.roles == hello.roles
