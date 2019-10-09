from stilio.crawler.dht.node import Node


class TestNode:
    def setup_method(self):
        self.node = Node.create_random("192.168.1.1", 8000)

    def test_create_random(self) -> None:
        assert self.node.address == "192.168.1.1"
        assert self.node.port == 8000

    def test_generate_random_id(self) -> None:
        assert len(Node.generate_random_id()) == 20

    def test_hex_id(self) -> None:
        assert self.node.hex_id == self.node.nid.hex()

    def test_eq(self) -> None:
        random_id = Node.generate_random_id()
        assert Node(random_id, "192.168.1.1", 8000) == Node(
            random_id, "192.168.1.1", 8000
        )
        assert Node(random_id, "192.168.1.2", 8000) != Node(
            random_id, "192.168.1.1", 8000
        )
        assert Node(random_id, "192.168.1.1", 8000) != Node(
            random_id, "192.168.1.1", 8001
        )
        assert Node(random_id, "192.168.1.1", 8000) != Node(
            Node.generate_random_id(), "192.168.1.1", 8001
        )

    def test_repr(self) -> None:
        assert repr(self.node) == self.node.nid.hex()
