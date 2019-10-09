from random import random

from stilio.crawler.bittorrent.constants import PEER_ID_PREFIX, BT_PROTOCOL_PREFIX


def get_random_peer_id() -> bytes:
    """
    Returns a random peer_id e.g -SL0001-437266776182, where
    the first 8 bytes represent the identification of our client and
    it's version.
    """
    client_instance_id = "".join(
        str(int(10 * random())) for _ in range(20 - len(PEER_ID_PREFIX))
    )
    return bytes(f"{PEER_ID_PREFIX}{client_instance_id}", encoding="utf-8")


def has_bt_protocol_prefix(message: bytes) -> bool:
    """
    Checks if the peer response has the BT protocol prefix.
    """
    return message[:20] == BT_PROTOCOL_PREFIX[:20]


def is_extension_handshake_message(message: bytes) -> bool:
    return message[0] == 20 and message[1] == 0


def is_extension_message(message: bytes) -> bool:
    return message[0] == 20 and message[1] == 1


def is_handshake_valid(message: bytes, info_hash: bytes) -> bool:
    """
    Checks the information of the handshake to see if the peer
    is eligible to share metadata.
    """
    return (
        has_bt_protocol_prefix(message)
        and is_info_hash_valid(message, info_hash)
        and supports_metadata_exchange(message)
    )


def is_info_hash_valid(data: bytes, info_hash: bytes) -> bool:
    """
    Checks if the info_hash sent by another peer matches ours.
    """
    return data[28:48] == info_hash


def is_metadata_size_valid(message_dict: dict, max_metadata_size: int):
    metadata_size = message_dict[b"metadata_size"]
    return 0 < metadata_size < max_metadata_size


def supports_metadata_exchange(message: bytes) -> bool:
    """
    Check using the peer response if it supports the metadata
    exchange protocol extension.
    """
    return message[25] == 16
