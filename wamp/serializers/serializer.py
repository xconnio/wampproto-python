from wamp.messages.hello import Hello
from wamp.messages.abort import Abort
from wamp.messages.welcome import Welcome
from wamp.messages.goodbye import Goodbye
from wamp.messages.message import Message
from wamp.messages.challenge import Challenge
from wamp.messages.authenticate import Authenticate


class Serializer:
    def serialize(self, message: Message) -> bytes:
        raise NotImplementedError()

    def deserialize(self, message: Message) -> Message:
        raise NotImplementedError()


def to_message(message: list) -> Message:
    if not isinstance(message, list):
        raise TypeError(f"invalid type '{type(message)}', expected a list")

    message_type = message[0]
    if not isinstance(message_type, int):
        raise TypeError(f"invalid message type '{type(message[0])}', expected an integer")

    match message_type:
        case 1:
            return Hello.parse(message)

        case 2:
            return Welcome.parse(message)

        case 3:
            return Abort.parse(message)

        case 4:
            return Challenge.parse(message)

        case 5:
            return Authenticate.parse(message)

        case 6:
            return Goodbye.parse(message)

        case _:
            raise ValueError("unknown message type")
