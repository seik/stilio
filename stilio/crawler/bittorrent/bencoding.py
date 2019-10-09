from __future__ import annotations

from io import BytesIO
from typing import Any

import better_bencode

KRPCTypes = Any
KRPCList = Any
KRPCDict = Any


class BencoderError(Exception):
    pass


def encode(obj: Any) -> bytes:
    try:
        return better_bencode.dumps(obj)
    except Exception as e:
        raise BencoderError(e)


def decode(bytes_object: bytes) -> Any:
    try:
        return better_bencode.loads(bytes_object)
    except Exception as e:
        raise BencoderError(e)


def decode2(bytes_object: bytes) -> Any:
    bytes_io = BytesIO(bytes_object)
    try:
        return better_bencode.load(bytes_io), bytes_io.tell()
    except Exception as e:
        raise BencoderError(e)
