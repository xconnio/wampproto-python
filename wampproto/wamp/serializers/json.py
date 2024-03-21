import json

from wampproto.wamp.messages.message import Message
from wamp.serializers.serializer import to_message
from wamp.serializers.serializer import Serializer


class JSONSerializer(Serializer):
    def serialize(self, message: Message) -> bytes:
        json_str = json.dumps(message.marshal())
        return json_str.encode("utf-8")

    def deserialize(self, data: bytes) -> Message:
        json_str = data.decode("utf-8")
        wamp_message = json.loads(json_str)
        return to_message(wamp_message)
