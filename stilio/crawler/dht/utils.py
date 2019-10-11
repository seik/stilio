import ipaddress
from socket import inet_ntoa
from typing import List, cast

from stilio.crawler.dht.node import Node


def decode_nodes(encoded_nodes: List[bytes]) -> List[Node]:
    """
    Converts a List[bytes] into List[Node].
    """
    decoded_nodes = []

    for i in range(0, len(encoded_nodes), 26):
        bytes_node = cast(bytes, encoded_nodes[i: i + 26])

        nid = cast(bytes, bytes_node[:20])
        address = inet_ntoa(bytes_node[20:24])
        port = int.from_bytes(bytes_node[24:], "big")

        node = Node(nid=nid, address=address, port=port)
        decoded_nodes.append(node)

    return decoded_nodes


def generate_neighbor_nid(local_nid: bytes, neighbour_nid: bytes) -> bytes:
    """
    Generates a fake node id adding the first 15 bytes of the local node and
    the first 5 bytes of the remote node.

    This makes the remote node believe we are close to it in the DHT.
    """
    return neighbour_nid[:15] + local_nid[:5]


def is_valid_node(local_node: Node, remote_node: Node) -> bool:
    """
    Checks if the node is valid, which means:
     - local_node != remote_node and the
     - remote_node port being in a valid range, in this case: ]0, 65536[ .
     - IP is not protected
    """
    return (
            remote_node != local_node
            and remote_node.is_valid_port
            and remote_node.is_address_private
    )
