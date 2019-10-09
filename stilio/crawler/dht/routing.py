from __future__ import annotations

from typing import List

from stilio.crawler.dht.node import Node


class RoutingTable:
    def __init__(self, max_size: int):
        self.max_size = max_size
        self.nodes: List[Node] = []

    @property
    def is_full(self) -> bool:
        return len(self.nodes) > self.max_size

    def add(self, node: Node) -> bool:
        if not self.is_full:
            self.nodes.append(node)
        return not self.is_full
