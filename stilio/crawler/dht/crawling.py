from __future__ import annotations

import asyncio
import logging
from typing import Tuple, List

from stilio.config import (
    CRAWLER_DEBUG_LEVEL,
    CRAWLER_ADDRESS,
    CRAWLER_PORT,
    CRAWLER_BOOTSTRAP_NODES,
)
from stilio.crawler.bittorrent.bencoding import decode, BencoderError
from stilio.crawler.bittorrent.metadata import MetadataFetcher
from stilio.crawler.dht import utils as dht_utils
from stilio.crawler.dht.dispatcher import DHTDispatcher
from stilio.crawler.dht.node import Node
from stilio.crawler.dht.routing import RoutingTable
from stilio.crawler.dht.rpc import RPC
from stilio.persistence import utils as db_utils
from stilio.persistence.exceptions import PersistenceError

logging.basicConfig(level=CRAWLER_DEBUG_LEVEL)
logger = logging.getLogger(__name__)


class CrawlingService(DHTDispatcher):
    def __init__(self, max_neighbors: int = 500, tick_interval: int = 1):
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
        for address in CRAWLER_BOOTSTRAP_NODES:
            self.rpc.find_node(self.node.nid, address=address)

    def _make_neighbours(self) -> None:
        for node in self.routing_table.nodes:
            neighbour_nid = dht_utils.generate_neighbor_nid(self.node.nid, node.nid)
            self.rpc.find_node(neighbour_nid, address=(node.address, node.port))

    async def _tick_periodically(self) -> None:
        while self._running:
            await asyncio.sleep(self._tick_interval)

            if not self.routing_table.nodes:
                await self._bootstrap()

            self._make_neighbours()
            self.routing_table.nodes.clear()

            self.routing_table.max_size = self.routing_table.max_size * 101 // 100

            logging.debug(f"Max number of neighbours is {self.routing_table.max_size}")
            logger.info(f"Active tasks: {len(asyncio.Task.all_tasks())}")

    def on_announce_peer(
        self, tid: bytes, nid: bytes, info_hash: bytes, address: Tuple[str, int]
    ) -> None:
        self.rpc.respond_announce_peer(
            tid=tid,
            nid=dht_utils.generate_neighbor_nid(self.node.nid, nid),
            address=address,
        )
        logger.debug(f"On announce peer, infohash {info_hash}")

        # if not await Torrent.objects.filter(info_hash=info_hash).exists():
        self.metadata_fetcher.fetch(info_hash, address)

    def on_bandwidth_exhausted(self):
        if self.routing_table.max_size < 200:
            logging.warning(
                "Max number of neighbours is low (< 200) and congestion persists, please "
                "check your network if this message still occurs"
            )
        else:
            self.routing_table.max_size = self.routing_table.max_size * 9 // 10

    def on_find_node(self, nodes: List[Node]) -> None:
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
        logger.debug(f"On get peers, infohash {info_hash}")

    def on_metadata_result(self, info_hash: bytes, metadata: bytes) -> None:
        try:
            metadata_decoded = decode(metadata)
            asyncio.ensure_future(
                db_utils.store_metadata(info_hash, metadata_decoded, logger)
            )
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
