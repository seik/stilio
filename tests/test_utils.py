from stilio.crawler.dht.node import Node
from stilio.crawler.dht.utils import decode_nodes, generate_neighbor_nid


class TestUtilsBittorrent:
    def test_decode_nodes_success(self) -> None:
        encoded_nodes = (
            b"}\xe9P\x1d\x9ek\n\xfa\xfe\xc3 jc\xfa3\x1frtG\xb3:\xe06\x9c\x1fs"
        )
        nodes = decode_nodes(encoded_nodes)
        node = Node(
            nid=b"}\xe9P\x1d\x9ek\n\xfa\xfe\xc3 jc\xfa3\x1frtG\xb3",
            address="58.224.54.156",
            port=8051,
        )
        assert node.nid == nodes[0].nid
        assert node.address == nodes[0].address

    def test_generate_neighbor_nid(self) -> None:
        neighbor_nid = generate_neighbor_nid(
            b"}\xe9P\x1d\x9ek\n\xfa\xfe\xc3 jc\xfa3\x1frtG\xb3",
            b"$d\xff\x93uy\xfeN]\xd5/\xd5cQ\x7f\xce\xd7\xaf\xca\x1c",
        )
        assert neighbor_nid == b"$d\xff\x93uy\xfeN]\xd5/\xd5cQ\x7f}\xe9P\x1d\x9e"
