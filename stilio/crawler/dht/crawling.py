from __future__ import annotations

import asyncio
import logging
from typing import List, Tuple

from stilio.config import (
    CRAWLER_ADDRESS,
    CRAWLER_BOOTSTRAP_NODES,
    CRAWLER_DEBUG_LEVEL,
    CRAWLER_PORT,
)
from stilio.crawler.bittorrent.bencoding import BencoderError, decode
from stilio.crawler.bittorrent.metadata import MetadataFetcher
from stilio.crawler.dht import utils as dht_utils
from stilio.crawler.dht.dispatcher import DHTDispatcher
from stilio.crawler.dht.node import Node
from stilio.crawler.dht.routing import RoutingTable
from stilio.crawler.dht.rpc import RPC
from stilio.persistence import utils as db_utils
from stilio.persistence.exceptions import PersistenceError
from stilio.persistence.torrents.models import Torrent

logging.basicConfig(level=CRAWLER_DEBUG_LEVEL)
logger = logging.getLogger(__name__)


class CrawlingService(DHTDispatcher):
    def __init__(self, max_neighbors: int = 500, tick_interval: int = 1):
        """Args:

            max_neighbors: maximum number of neighbors in the crawling service 
            tick_interval: number of seconds between every attempt to get new neighbors 
        """
        self.node = Node.create_random(CRAWLER_ADDRESS, CRAWLER_PORT)

        self.rpc: RPC = RPC()
        self.rpc.on_bandwidth_exhausted = self.on_bandwidth_exhausted

        self.routing_table: RoutingTable = RoutingTable(max_neighbors)

        self.loop = asyncio.get_event_loop()

        self._tick_interval = tick_interval

        self.metadata_fetcher = MetadataFetcher(
            on_metadata_result=self.on_metadata_result
        )

        super().__init__(self.rpc)

    async def _bootstrap(self) -> None:
        """Bootstrap the crawler with some default nodes
        """
        for address in CRAWLER_BOOTSTRAP_NODES:
            self.rpc.find_node(self.node.nid, address=address)

    def _make_neighbors(self) -> None:
        for node in self.routing_table.nodes:
            neighbor_nid = dht_utils.generate_neighbor_nid(self.node.nid, node.nid)
            self.rpc.find_node(neighbor_nid, address=(node.address, node.port))

    async def _tick_periodically(self) -> None:
        while self._running:
            await asyncio.sleep(self._tick_interval)

            if not self.routing_table.nodes:
                await self._bootstrap()

            self._make_neighbors()
            self.routing_table.nodes.clear()

            self.routing_table.max_size = self.routing_table.max_size * 101 // 100

            logging.debug(f"Max number of neighbors is {self.routing_table.max_size}")
            logger.info(f"Active tasks: {len(asyncio.Task.all_tasks())}")

    def on_announce_peer(
        self, tid: bytes, nid: bytes, info_hash: bytes, address: Tuple[str, int]
    ) -> None:
        """Peer found, respond with a fake node id"""
        self.rpc.respond_announce_peer(
            tid=tid,
            nid=dht_utils.generate_neighbor_nid(self.node.nid, nid),
            address=address,
        )
        logger.debug(f"On announce peer, infohash {info_hash.hex()}")

        if not Torrent.exists(info_hash):
            self.metadata_fetcher.fetch(info_hash, address)

    def on_bandwidth_exhausted(self):
        """Bandwidth is being exhausted, reduce the number of nodes or warn the user
        if this number is already too low
        """
        if self.routing_table.max_size < 200:
            logging.warning(
                "Max number of neighbors is low (< 200) and congestion persists, please "
                "check your network if this message still occurs"
            )
        else:
            self.routing_table.max_size = self.routing_table.max_size * 9 // 10

    def on_find_node(self, nodes: List[Node]) -> None:
        """Found a node, if the table is not full and the node is not in the routing
        table already, add it
        """
        if not self.routing_table.is_full:
            nodes = [node for node in nodes if self.node != node and node.is_valid]
            for node in nodes:
                self.routing_table.add(node)

    def on_get_peers(
        self, info_hash: bytes, tid: bytes, address: Tuple[str, int]
    ) -> None:
        self.rpc.respond_get_peers(
            tid=tid, info_hash=info_hash, nid=self.node.nid, address=address
        )
        logger.debug(f"On get peers, infohash {info_hash.hex()}")

    def on_metadata_result(self, info_hash: bytes, metadata: bytes) -> None:
        """Received metadata (aka torrent info), decode it and store in db"""
        try:
            metadata_decoded = decode(metadata)
            db_utils.store_metadata(info_hash, metadata_decoded, logger)
        except (asyncio.CancelledError, BencoderError, PersistenceError):
            pass
        except Exception as e:
            logger.debug("Error retrieving metadata")
            logger.exception(e)

    def run(self) -> None:
        self._running = True

        self.loop.run_until_complete(self.rpc.start())
        asyncio.ensure_future(self._tick_periodically())

        self.loop.run_forever()
        self.loop.close()

    def stop(self) -> None:
        self._running = False
        self.loop.call_later(self._tick_interval, self.loop.stop)
