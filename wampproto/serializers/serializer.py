from wampproto import messages


class Serializer:
    def serialize(self, message: messages.Message) -> bytes:
        raise NotImplementedError()

    def deserialize(self, data: bytes | str) -> messages.Message:
        raise NotImplementedError()


def to_message(message: list) -> messages.Message:
    if not isinstance(message, list):
        raise TypeError(f"invalid type '{type(message)}', expected a list")

    message_type = message[0]
    if not isinstance(message_type, int):
        raise TypeError(f"invalid message type '{type(message[0])}', expected an integer")

    match message_type:
        case messages.Hello.TYPE:
            return messages.Hello.parse(message)
        case messages.Welcome.TYPE:
            return messages.Welcome.parse(message)
        case messages.Abort.TYPE:
            return messages.Abort.parse(message)
        case messages.Challenge.TYPE:
            return messages.Challenge.parse(message)
        case messages.Authenticate.TYPE:
            return messages.Authenticate.parse(message)
        case messages.Goodbye.TYPE:
            return messages.Goodbye.parse(message)
        case _:
            raise ValueError("unknown message type")
