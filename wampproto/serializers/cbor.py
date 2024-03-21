import cbor2

from wampproto.messages import Message
from wampproto.serializers.serializer import to_message
from wampproto.serializers.serializer import Serializer


class CBORSerializer(Serializer):
    def serialize(self, message: Message) -> bytes:
        return cbor2.dumps(message.marshal())

    def deserialize(self, data: bytes) -> Message:
        wamp_message = cbor2.loads(data)
        return to_message(wamp_message)
