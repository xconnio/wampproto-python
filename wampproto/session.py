from wampproto import messages, serializers


class WAMPSession:
    def __init__(self, serializer: serializers.Serializer = serializers.JSONSerializer()):
        self._serializer = serializer

        # data structures for RPC
        self._call_requests: set[int] = set()
        self._register_requests: set[int] = set()
        self._registrations: set[int] = set()
        self._invocation_requests: set[int] = set()
        self._unregister_requests: dict[int, int] = {}
        # data structures for PubSub
        self._publish_requests: set[int] = set()
        self._subscribe_requests: set[int] = set()
        self._subscriptions: set[int] = set()
        self._unsubscribe_requests: dict[int, int] = {}

    def send_message(self, msg: messages.Message) -> bytes:
        if isinstance(msg, messages.Call):
            self._call_requests.add(msg.request_id)
        elif isinstance(msg, messages.Register):
            self._register_requests.add(msg.request_id)
        elif isinstance(msg, messages.Unregister):
            self._unregister_requests[msg.request_id] = msg.registration_id
        elif isinstance(msg, messages.Yield):
            if msg.request_id not in self._invocation_requests:
                raise ValueError("cannot yield for unknown invocation request")

            self._invocation_requests.remove(msg.request_id)
        elif isinstance(msg, messages.Publish):
            if msg.options.get("acknowledge", False):
                self._publish_requests.add(msg.request_id)
        elif isinstance(msg, messages.Subscribe):
            self._subscribe_requests.add(msg.request_id)
        elif isinstance(msg, messages.Unsubscribe):
            self._unsubscribe_requests[msg.request_id] = msg.subscription_id
        elif isinstance(msg, messages.Error):
            if msg.message_type != messages.Invocation.TYPE:
                raise ValueError("send only supported for invocation error")

            self._invocation_requests.discard(msg.request_id)
        elif isinstance(msg, messages.Goodbye):
            pass
        else:
            raise ValueError(f"unknown message type {type(msg)}")

        return self._serializer.serialize(msg)

    def receive(self, data: bytes) -> messages.Message:
        msg = self._serializer.deserialize(data)
        return self.receive_message(msg)

    def receive_message(self, msg: messages.Message) -> messages.Message:
        if isinstance(msg, messages.Result):
            try:
                self._call_requests.remove(msg.request_id)
            except KeyError:
                raise ValueError("received RESULT for invalid request_id")
        elif isinstance(msg, messages.Registered):
            try:
                self._register_requests.remove(msg.request_id)
            except KeyError:
                raise ValueError("received REGISTERED for invalid request_id")

            self._registrations.add(msg.registration_id)
        elif isinstance(msg, messages.Unregistered):
            try:
                registration_id = self._unregister_requests.pop(msg.request_id)
            except KeyError:
                raise ValueError("received UNREGISTERED for invalid request_id")

            try:
                self._registrations.remove(registration_id)
            except KeyError:
                raise ValueError("received UNREGISTERED for invalid registration_id")
        elif isinstance(msg, messages.Invocation):
            if msg.registration_id not in self._registrations:
                raise ValueError("received INVOCATION for invalid registration_id")

            self._invocation_requests.add(msg.request_id)
        elif isinstance(msg, messages.Published):
            try:
                self._publish_requests.remove(msg.request_id)
            except KeyError:
                raise ValueError("received PUBLISHED for invalid registration_id")
        elif isinstance(msg, messages.Subscribed):
            try:
                self._subscribe_requests.remove(msg.request_id)
            except KeyError:
                raise ValueError("received SUBSCRIBED for invalid request_id")

            self._subscriptions.add(msg.subscription_id)
        elif isinstance(msg, messages.Unsubscribed):
            try:
                subscription_id = self._unsubscribe_requests.pop(msg.request_id)
            except KeyError:
                raise ValueError("received UNSUBSCRIBED for invalid request_id")

            try:
                self._subscriptions.remove(subscription_id)
            except KeyError:
                raise ValueError("received UNSUBSCRIBED for invalid subscription_id")
        elif isinstance(msg, messages.Event):
            if msg.subscription_id not in self._subscriptions:
                raise ValueError("received EVENT for invalid subscription_id")
        elif isinstance(msg, messages.Error):
            match msg.message_type:
                case messages.Call.TYPE:
                    try:
                        self._call_requests.remove(msg.request_id)
                    except KeyError:
                        raise ValueError("received ERROR for invalid call request")
                case messages.Register.TYPE:
                    try:
                        self._register_requests.remove(msg.request_id)
                    except KeyError:
                        raise ValueError("received ERROR for invalid register request")
                case messages.Unregister.TYPE:
                    try:
                        self._unregister_requests.pop(msg.request_id)
                    except KeyError:
                        raise ValueError("received ERROR for invalid unregister request")
                case messages.Subscribe.TYPE:
                    try:
                        self._subscribe_requests.remove(msg.request_id)
                    except KeyError:
                        raise ValueError("received ERROR for invalid subscribe request")
                case messages.Unsubscribe.TYPE:
                    try:
                        self._unsubscribe_requests.pop(msg.request_id)
                    except KeyError:
                        raise ValueError("received ERROR for invalid unsubscribe request")
                case messages.Publish.TYPE:
                    try:
                        self._publish_requests.remove(msg.request_id)
                    except KeyError:
                        raise ValueError("received ERROR for invalid publish request")
                case _:
                    raise ValueError(f"unknown error message type {type(msg)}")
        elif isinstance(msg, messages.Goodbye):
            return msg
        elif isinstance(msg, messages.Abort):
            return msg
        else:
            raise ValueError(f"unknown message {type(msg)}")

        return msg
