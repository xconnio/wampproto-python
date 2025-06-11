import math

MAGIC = 0x7F
# 16 megabyte
PROTOCOL_MAX_MSG_SIZE = 2**24
DEFAULT_MAX_MSG_SIZE = 2**20

SERIALIZER_TYPE_JSON = 1
SERIALIZER_TYPE_MSGPACK = 2
SERIALIZER_TYPE_CBOR = 3

MSG_TYPE_WAMP = 0
MSG_TYPE_PING = 1
MSG_TYPE_PONG = 2


class Handshake:
    def __init__(self, protocol: int, max_msg_size: int):
        super().__init__()
        self._protocol = protocol
        self._max_msg_size = max_msg_size

    @property
    def protocol(self) -> int:
        return self._protocol

    @property
    def max_msg_size(self) -> int:
        return self._max_msg_size

    def to_bytes(self) -> bytes:
        return send_handshake(self)

    @classmethod
    def from_bytes(cls, data: bytes) -> "Handshake":
        return receive_handshake(data)


class MessageHeader:
    def __init__(self, kind: int, length: int):
        super().__init__()
        self._kind = kind
        self._length = length

    @property
    def kind(self) -> int:
        return self._kind

    @property
    def length(self) -> int:
        return self._length

    def to_bytes(self) -> bytes:
        data = int_to_bytes(self._length)
        return bytes(
            [
                self._kind,
                data[0],
                data[1],
                data[2],
            ]
        )

    @classmethod
    def from_bytes(cls, data: bytes) -> "MessageHeader":
        return MessageHeader(data[0], bytes_to_int(data[1:]))


def send_handshake(hs: Handshake) -> bytes:
    # FIXME: max_msg_size must not be more than 16 megabytes.
    # FIXME: protocol must be checked to ensure only supported serializers are used.

    return bytes(
        [
            MAGIC,
            int(math.log2(hs.max_msg_size)) - 9 << 4 | (hs.protocol & 0xF),
            0x00,
            0x00,
        ]
    )


def receive_handshake(data: bytes) -> Handshake:
    if len(data) != 4:
        raise ValueError("Expected 4 bytes for handshake response, got %d" % len(data))

    if data[0] != MAGIC:
        raise ValueError("Expected MAGIC, got %d" % data[0])

    if data[2] != 0x00 and data[3] != 0x00:
        raise ValueError(f"Expected 0x00 for third and fourth byte of handshake response, got {data[2]} and {data[3]}")

    return Handshake(data[1] & 0x0F, 1 << ((data[1] >> 4) + 9))


def int_to_bytes(i: int) -> bytes:
    return bytes(
        [
            (i >> 16) & 0xFF,
            (i >> 8) & 0xFF,
            i & 0xFF,
        ]
    )


def bytes_to_int(b: bytes) -> int:
    n = 0
    shift = 0
    for byte in reversed(b):
        n |= byte << shift
        shift += 8

    return n
