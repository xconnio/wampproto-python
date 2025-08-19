import json
from typing import Any, Tuple

import cbor2
import msgpack

from wampproto import serializers


def decode(arr: list) -> Tuple[list[Any] | None, dict[Any, Any] | None]:
    if len(arr) == 0:
        return None, None

    if len(arr) > 2:
        raise ValueError("too many args to decode")

    args = arr[0]
    if not isinstance(args, list):
        raise TypeError("args element is not list")

    kwargs = None
    if len(arr) == 2:
        if not isinstance(arr[1], dict):
            raise TypeError("kwargs element is not dict")
        kwargs = arr[1]

    return args, kwargs


def prepare_for_encode(args: list | None = None, kwargs: dict | None = None) -> list | None:
    data = []
    if args is not None:
        data.append(args)

    if kwargs is not None:
        if args is None:
            data.append([])
        data.append(kwargs)

    return data if data is not None else None


def cbor_encode_payload(args: list, kwargs: dict) -> bytes | None:
    data = prepare_for_encode(args, kwargs)
    if data is None:
        return None

    return cbor2.dumps(data)


def cbor_decode_payload(b: bytes) -> Tuple[list[Any] | None, dict[Any, Any] | None]:
    if len(b) == 0:
        return None, None

    arr = cbor2.loads(b)

    return decode(arr)


def msgpack_encode_payload(args: list, kwargs: dict) -> bytes | None:
    data = prepare_for_encode(args, kwargs)
    if data is None:
        return None

    return msgpack.dumps(data)


def msgpack_decode_payload(b: bytes) -> Tuple[list[Any] | None, dict[Any, Any] | None]:
    if len(b) == 0:
        return None, None

    arr = msgpack.loads(b)

    return decode(arr)


def json_encode_payload(args: list, kwargs: dict) -> bytes | None:
    data = prepare_for_encode(args, kwargs)
    if data is None:
        return None

    return json.dumps(data).encode()


def json_decode_payload(b: bytes) -> Tuple[list[Any] | None, dict[Any, Any] | None]:
    if len(b) == 0:
        return None, None

    arr = json.loads(b)

    return decode(arr)


def deserialize_payload(serializer_id: int, payload: bytes) -> Tuple[list[Any] | None, dict[Any, Any] | None]:
    match serializer_id:
        case serializers.NONE_SERIALIZER_ID:
            return [payload], {}
        case serializers.JSON_SERIALIZER_ID:
            return json_decode_payload(payload)
        case serializers.CBOR_SERIALIZER_ID:
            return cbor_decode_payload(payload)
        case serializers.MSGPACK_SERIALIZER_ID:
            return msgpack_decode_payload(payload)
        case _:
            raise ValueError(f"serializer {serializer_id} not recognized")


def serialize_payload(serializer_id: int, args: list, kwargs: dict) -> bytes | None:
    match serializer_id:
        case serializers.NONE_SERIALIZER_ID:
            if args is None and kwargs is None:
                return None

            if len(args) != 1 or kwargs:
                raise ValueError(f"serializer {serializer_id} requires exactly 1 arg")

            payload = args[0]
            if not isinstance(payload, (bytes, bytearray)):
                raise TypeError(f"serializer {serializer_id} requires bytes")

            return payload

        case serializers.JSON_SERIALIZER_ID:
            return json_encode_payload(args, kwargs)
        case serializers.CBOR_SERIALIZER_ID:
            return cbor_encode_payload(args, kwargs)
        case serializers.MSGPACK_SERIALIZER_ID:
            return msgpack_encode_payload(args, kwargs)
        case _:
            raise ValueError(f"serializer {serializer_id} not recognized")
