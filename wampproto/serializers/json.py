import json

from wampproto import messages, serializers
from wampproto.serializers.serializer import to_message


class JSONSerializer(serializers.Serializer):
    def serialize(self, message: messages.Message) -> bytes:
        json_str = json.dumps(message.marshal())
        return json_str.encode("utf-8")

    def deserialize(self, data: bytes | str) -> messages.Message:
        if isinstance(data, bytes):
            data = data.decode("utf-8")
        wamp_message = json.loads(data)
        return to_message(wamp_message)
