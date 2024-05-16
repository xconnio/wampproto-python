import json

from wampproto import messages, serializers
from wampproto.serializers.serializer import to_message


class JSONSerializer(serializers.Serializer):
    def serialize(self, message: messages.Message) -> str:
        return json.dumps(message.marshal())

    def deserialize(self, data: str) -> messages.Message:
        wamp_message = json.loads(data)
        return to_message(wamp_message)
