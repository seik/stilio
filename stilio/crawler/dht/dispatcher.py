from __future__ import annotations

from abc import abstractmethod
from typing import List, Tuple

from stilio.crawler.bittorrent.bencoding import KRPCTypes
from stilio.crawler.dht import utils as dht_utils
from stilio.crawler.dht.node import Node
from stilio.crawler.dht.rpc import RPC


class DHTDispatcher:
    def __init__(self, rpc: RPC):
        self._running = True

        rpc.on_response = self.on_response

    def _validate_on_announce_peer(self, data):
        return (
            b"a" in data
            and b"id" in data[b"a"]
            and b"t" in data
            and b"info_hash" in data[b"a"]
            and b"port" in data[b"a"]
        )

    def _validate_on_find_node(self, encoded_nodes):
        return len(encoded_nodes) % 26 == 0

    def _validate_on_get_peers(self, data):
        return b"a" in data and b"info_hash" in data[b"a"] and b"t" in data

    @abstractmethod
    def on_announce_peer(
        self, tid: bytes, nid: bytes, info_hash: bytes, address: Tuple[str, int]
    ) -> None:
        pass

    @abstractmethod
    def on_find_node(self, nodes: List[Node]) -> None:
        pass

    @abstractmethod
    def on_get_peers(
        self, info_hash: bytes, tid: bytes, address: Tuple[str, int]
    ) -> None:
        pass

    def on_response(self, data: KRPCTypes, address: Tuple[str, int]) -> None:
        if not self._running:
            return
        elif (
            isinstance(data.get(b"r"), dict) and type(data[b"r"].get(b"nodes")) is bytes
        ):
            encoded_nodes = data[b"r"][b"nodes"]
            if self._validate_on_find_node(encoded_nodes):
                decoded_nodes = dht_utils.decode_nodes(encoded_nodes)
                self.on_find_node(decoded_nodes)
        elif data.get(b"q") == b"get_peers" and self._validate_on_get_peers(data):
            info_hash = data[b"a"][b"info_hash"]
            tid = data[b"t"]

            self.on_get_peers(info_hash, tid, address)
        elif data.get(b"q") == b"announce_peer" and self._validate_on_announce_peer(
            data
        ):
            nid = data[b"a"][b"id"]
            tid = data[b"t"]
            info_hash = data[b"a"][b"info_hash"]
            port = data[b"a"][b"port"]

            implied_port = (
                data[b"a"][b"implied_port"] if b"implied_port" in data[b"a"] else None
            )
            remote_address = (
                (address[0], address[1]) if implied_port else (address[0], port)
            )

            self.on_announce_peer(
                nid=nid, tid=tid, info_hash=info_hash, address=remote_address
            )
