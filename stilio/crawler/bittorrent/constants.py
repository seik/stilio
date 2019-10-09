# Handshake
"""
PSTR: String identifier of the Bittorrent protocol V1, 19 bytes.
PSTR_LEN: PSTR length, 1 byte.
RESERVED: 8 bytes, zeroes for example.
PEER_ID_PREFIX: 8 bytes used as an unique ID for the client. "SL" is the
                peer_id chosen for this client. The full PEER_ID is 20 bytes,
                the rest of it is built using random numbers.

The full handshake message consists of:

<PSTR_LEN><PSTR><RESERVED><INFO_HASH><PEER_ID>

The full handshake consists of 68 bytes.
"""
from stilio.crawler.bittorrent.bencoding import encode

PSTR = "BitTorrent protocol"
PSTR_LEN = chr(len(PSTR))
RESERVED = "\x00\x00\x00\x00\x00\x10\x00\x01"
PEER_ID_PREFIX = "-SL0001-"
BT_PROTOCOL_PREFIX = bytes(PSTR_LEN + PSTR + RESERVED, encoding="utf-8")

# Extension
ID_EXTENDED_MESSAGE = 20
ID_EXTENDED_HANDSHAKE = 0
EXTENDED_HANDSHAKE_MESSAGE = bytes(
    [ID_EXTENDED_MESSAGE, ID_EXTENDED_HANDSHAKE]
) + encode({b"m": {b"ut_metadata": 1}})
