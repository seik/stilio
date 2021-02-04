from __future__ import annotations

import os
from ipaddress import ip_address


class Node:
    def __init__(self, nid: bytes, address: str, port: int):
        self.nid = nid
        self.address = address
        self.port = port

    @property
    def hex_id(self) -> str:
        return self.nid.hex()

    @property
    def is_address_public(self) -> bool:
        return not ip_address(self.address).is_private

    @property
    def is_valid(self) -> bool:
        return self.is_address_public and self.is_valid_port

    @property
    def is_valid_port(self) -> bool:
        return 0 < self.port < 65536

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Node):
            return (
                self.nid == other.nid
                and self.address == other.address
                and self.port == other.port
            )
        return False

    def __repr__(self) -> str:
        """
        Represents the node in an hex format using the nid.
        """
        return self.hex_id

    @classmethod
    def create_random(cls, address: str, port: int) -> Node:
        """
        Creates a random node with the desired address and port.
        """
        nid = Node.generate_random_id()
        return cls(nid, address, port)

    @staticmethod
    def generate_random_id() -> bytes:
        """
        Generates a random node id which consists of 20 bytes.
        """
        return os.urandom(20)
