import logging
from socket import inet_ntoa
from typing import List, cast

from stilio.config import CRAWLER_DEBUG_LEVEL
from stilio.crawler.dht.node import Node

logging.basicConfig(level=CRAWLER_DEBUG_LEVEL)
logger = logging.getLogger(__name__)


def decode_nodes(encoded_nodes: bytes) -> List[Node]:
    """
    Converts a List[bytes] into List[Node].
    """
    decoded_nodes = []
    for i in range(0, len(encoded_nodes), 26):
        bytes_node = cast(bytes, encoded_nodes[i : i + 26])

        nid = bytes_node[:20]

        try:
            address = inet_ntoa(bytes_node[20:24])
        except OSError:
            logger.debug("Error parsing a node, continuing...")
            continue

        port = int.from_bytes(bytes_node[24:], "big")

        node = Node(nid=nid, address=address, port=port)
        decoded_nodes.append(node)
    return decoded_nodes


def generate_neighbor_nid(local_nid: bytes, neighbor_nid: bytes) -> bytes:
    """
    Generates a fake node id adding the first 15 bytes of the local node and
    the first 5 bytes of the remote node.

    This makes the remote node believe we are close to it in the DHT.
    """
    return neighbor_nid[:15] + local_nid[:5]
