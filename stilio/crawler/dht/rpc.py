from __future__ import annotations

from typing import Callable, Optional, Tuple

from stilio.crawler.bittorrent.bencoding import BencoderError, KRPCTypes, decode, encode
from stilio.crawler.dht.constants import TOKEN_LENGTH
from stilio.crawler.dht.node import Node
from stilio.crawler.dht.udp import UDPNode


class RPC:
    def __init__(self) -> None:
        self.udp_node = UDPNode()
        self.udp_node.on_data_received = self._on_data_received
        self.udp_node.on_bandwidth_exhausted = self._on_bandwidth_exhausted

        # Callbacks
        self.on_response: Optional[Callable[[KRPCTypes, Tuple[str, int]], None]] = None
        self.on_bandwidth_exhausted: Optional[Callable[[], None]] = None

    def _on_data_received(self, data: bytes, address: Tuple[str, int]):
        # If port is 0 skip since it cannot be reached
        if address[1] == 0:
            return

        try:
            message = decode(data)
        except BencoderError:
            return

        if self.on_response:
            self.on_response(message, address)

    def _on_bandwidth_exhausted(self):
        if self.on_bandwidth_exhausted:
            self.on_bandwidth_exhausted()

    def find_node(self, nid: bytes, address: Tuple[str, int]) -> None:
        data = {
            b"y": b"q",
            b"q": b"find_node",
            b"t": b"aa",
            b"a": {b"id": nid, b"target": Node.generate_random_id()},
        }
        self.send_message(data, address)

    def send_message(self, data: dict, address: Tuple[str, int]) -> None:
        try:
            message = encode(data)
        except BencoderError:
            pass
        else:
            self.udp_node.send_message(message, address)

    async def start(self):
        await self.udp_node.start()

    def respond_announce_peer(
        self, tid: bytes, nid: bytes, address: Tuple[str, int]
    ) -> None:
        data = {b"y": b"r", b"t": tid, b"r": {b"id": nid}}
        self.send_message(data, address)

    def respond_get_peers(
        self, tid: bytes, info_hash: bytes, nid: bytes, address: Tuple[str, int]
    ) -> None:
        data = {
            b"y": b"r",
            b"t": tid,
            b"r": {
                b"id": info_hash[:15] + nid[:5],
                b"nodes": b"",
                b"token": info_hash[:TOKEN_LENGTH],
            },
        }
        self.send_message(data, address)
