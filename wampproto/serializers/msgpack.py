import msgpack

from wampproto import messages, serializers
from wampproto.serializers.serializer import to_message


class MsgPackSerializer(serializers.Serializer):
    def serialize(self, message: messages.Message) -> bytes:
        return msgpack.dumps(message.marshal())

    def deserialize(self, data: bytes) -> messages.Message:
        wamp_message = msgpack.loads(data)
        return to_message(wamp_message)
