from wamp.messages.hello import Hello
from wamp.serializers.json import JsonSerializer


def test_serializer():
    serializer = JsonSerializer()
    hello = Hello.parse([1, "realm1", {"roles": {"callee": {}}}])

    data = serializer.serialize(hello)
    assert isinstance(data, bytes)

    obj = serializer.deserialize(data)
    assert isinstance(obj, Hello)
    assert obj.realm == hello.realm
    assert obj.roles == hello.roles
