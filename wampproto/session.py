from wampproto import messages, serializers


class WAMPSession:
    def __init__(self, serializer: serializers.Serializer = serializers.JSONSerializer()):
        self._serializer = serializer

        self._call_requests: dict[int, int] = {}
        self._register_requests: dict[int, int] = {}
        self._registrations: dict[int, int] = {}
        self._invocation_requests: dict[int, int] = {}

    def send_message(self, msg: messages.Message) -> bytes:
        if isinstance(msg, messages.Call):
            data = self._serializer.serialize(msg)
            self._call_requests[msg.request_id] = msg.request_id
            return data
        elif isinstance(msg, messages.Register):
            data = self._serializer.serialize(msg)
            self._register_requests[msg.request_id] = msg.request_id
            return data
        elif isinstance(msg, messages.Yield):
            if msg.request_id not in self._invocation_requests:
                raise ValueError("cannot yield for unknown invocation request")

            data = self._serializer.serialize(msg)
            self._invocation_requests.pop(msg.request_id)
            return data

    def receive(self, data: bytes) -> messages.Message:
        msg = self._serializer.deserialize(data)
        return self.receive_message(msg)

    def receive_message(self, msg: messages.Message) -> messages.Message:
        if isinstance(msg, messages.Result):
            if msg.request_id not in self._call_requests:
                raise ValueError("received RESULT for invalid request_id")

            self._call_requests.pop(msg.request_id)

            return msg
        elif isinstance(msg, messages.Registered):
            if msg.request_id not in self._register_requests:
                raise ValueError("received REGISTERED for invalid request_id")

            self._register_requests.pop(msg.request_id)
            self._registrations[msg.registration_id] = msg.registration_id

            return msg
        elif isinstance(msg, messages.Invocation):
            if msg.registration_id not in self._registrations:
                raise ValueError("received INVOCATION for invalid registration_id")

            self._registrations.pop(msg.registration_id)
            self._invocation_requests[msg.request_id] = msg.request_id

            return msg
        else:
            raise ValueError(f"unknown message {type(msg)}")
