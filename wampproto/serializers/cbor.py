import cbor2

from wampproto import messages, serializers
from wampproto.serializers.serializer import to_message

CBOR_SERIALIZER_ID = 3


class CBORSerializer(serializers.Serializer):
    def serialize(self, message: messages.Message) -> bytes:
        return cbor2.dumps(message.marshal())

    def deserialize(self, data: bytes) -> messages.Message:
        wamp_message = cbor2.loads(data)
        return to_message(wamp_message)

    def static(self) -> bool:
        return False
