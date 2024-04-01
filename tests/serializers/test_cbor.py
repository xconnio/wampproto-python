from wampproto import messages, serializers


def test_serializer():
    serializer = serializers.CBORSerializer()
    hello = messages.Hello.parse([1, "realm1", {"roles": {"caller": {}}}])

    data = serializer.serialize(hello)
    assert isinstance(data, bytes)

    obj = serializer.deserialize(data)
    assert isinstance(obj, messages.Hello)
    assert obj.realm == hello.realm
    assert obj.roles == hello.roles
