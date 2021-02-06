import asyncio
import hashlib
import logging
import math
from asyncio import StreamReader, StreamWriter
from typing import Callable, Dict, Optional, Tuple

from stilio.config import (
    CRAWLER_DEBUG_LEVEL,
    CRAWLER_METADATA_FETCH_TIMEOUT,
    CRAWLER_METADATA_MAX_SIMULTANEOUS_WORKERS_PER_INFO_HASH,
)
from stilio.crawler.bittorrent import utils as bt_utils
from stilio.crawler.bittorrent.bencoding import BencoderError, decode, decode2, encode
from stilio.crawler.bittorrent.constants import (
    BT_PROTOCOL_PREFIX,
    EXTENDED_HANDSHAKE_MESSAGE,
    ID_EXTENDED_MESSAGE,
)
from stilio.crawler.bittorrent.exceptions import InvalidHandshake, InvalidMetadata
from stilio.crawler.bittorrent.utils import get_random_peer_id

logging.basicConfig(level=CRAWLER_DEBUG_LEVEL)
logger = logging.getLogger(__name__)

PeerAddress = Tuple[str, int]


class MetadataWorker:
    def __init__(
        self,
        info_hash: bytes,
        peer_address: PeerAddress,
        max_metadata_size: int = 10_000_000,
    ):
        self._peer_id = get_random_peer_id()
        self._peer_address = peer_address

        self._info_hash = info_hash

        self._reader: Optional[StreamReader] = None
        self._writer: Optional[StreamWriter] = None

        self._handshaked = False
        self._ut_metadata = int()

        self._max_metadata_size = max_metadata_size

        self._metadata_size = 0
        self._metadata_received = 0
        self._metadata = bytearray()

    def _on_extension_handshake_message(self, message: bytes) -> None:
        if self._handshaked:
            return

        try:
            message_dict = decode(message)
        except BencoderError:
            logger.debug(
                "Message in on_extension_handshake_message could not be decoded."
            )
            return

        try:
            ut_metadata = message_dict[b"m"][b"ut_metadata"]
            metadata_size = message_dict[b"metadata_size"]
        except KeyError:
            logger.debug(
                f"Missing ut_metadata or metadata_size in on_extension_handshake_message: {message_dict}."
            )
            return

        if not bt_utils.is_metadata_size_valid(message_dict, self._max_metadata_size):
            raise InvalidMetadata

        self._ut_metadata = ut_metadata
        try:
            self._metadata = bytearray(metadata_size)
        except MemoryError:
            logging.exception("Error trying to allocate the metadata in memory.")
            raise

        self._metadata_size = metadata_size
        self._handshaked = True

        pieces = math.ceil(self._metadata_size / (2 ** 14))
        for piece in range(pieces):
            self._request_piece(piece)

    def _on_extension_message(self, message: bytes) -> None:
        try:
            message_dict, i = decode2(message)
        except BencoderError:
            logger.debug("Message in on_extension_message could not be decoded.")
            return

        try:
            message_type = message_dict[b"msg_type"]
            piece = message_dict[b"piece"]
        except KeyError:
            logging.debug(
                f"Missing msg_type or piece in on_extension_message: {message_dict}."
            )
            return

        if message_type == 1:
            metadata_piece = message[i:]

            self._metadata[
                piece * 2 ** 14 : piece * 2 ** 14 + len(metadata_piece)
            ] = metadata_piece
            self._metadata_received += len(metadata_piece)

            if self._metadata_received == self._metadata_size:
                if hashlib.sha1(self._metadata).digest() == self._info_hash:
                    if not self._metadata_future.done():
                        self._metadata_future.set_result(bytes(self._metadata))
                else:
                    logging.debug("Invalid metadata in on_extension_message.")

        elif message_type == 2:
            logging.info("Peer rejected the connection.")

    def _on_handshake(self) -> None:
        """
        Sends to the peer the extended handshake message.
        """
        self._write_message(EXTENDED_HANDSHAKE_MESSAGE)

    def _on_message(self, message: bytes) -> None:
        if bt_utils.is_extension_handshake_message(message):
            self._on_extension_handshake_message(message[2:])

        if bt_utils.is_extension_message(message):
            self._on_extension_message(message[2:])

    def _request_piece(self, piece):
        message = bytes([ID_EXTENDED_MESSAGE, self._ut_metadata]) + encode(
            {b"msg_type": 0, b"piece": piece}
        )
        self._write_message(message)

    def _write_message(self, message: bytes):
        length = len(message).to_bytes(4, "big")
        if self._writer:
            self._writer.write(length + message)

    async def work(self):
        event_loop = asyncio.get_event_loop()
        self._metadata_future = event_loop.create_future()

        try:
            self._reader, self._writer = await asyncio.open_connection(
                *self._peer_address, loop=event_loop
            )

            self._writer.write(BT_PROTOCOL_PREFIX + self._info_hash + self._peer_id)

            message = await self._reader.readexactly(68)

            if not bt_utils.is_handshake_valid(message, self._info_hash):
                raise InvalidHandshake(
                    f"Invalid handshake for {self._info_hash.hex()} from peer {self._peer_address}."
                )

            self._on_handshake()

            while not self._metadata_future.done():
                buffer = await self._reader.readexactly(4)
                length = int.from_bytes(buffer, "big")
                message = await self._reader.readexactly(length)
                self._on_message(message)
        except ConnectionRefusedError:
            # If connection is refused just ignore it
            pass
        except Exception as e:
            logger.debug(
                f"There was an error retrieving metadata for {self._info_hash.hex()} from peer {self._peer_address}."
            )
            logger.exception(e)
        finally:
            if not self._metadata_future.done():
                self._metadata_future.set_result(None)

            if self._writer:
                self._writer.close()

        return self._metadata_future.result()


async def fetch_metadata(
    info_hash: bytes, peer_address: PeerAddress, max_metadata_size: int
) -> Optional[bytes]:
    try:
        result = await asyncio.wait_for(
            MetadataWorker(info_hash, peer_address, max_metadata_size).work(),
            timeout=CRAWLER_METADATA_FETCH_TIMEOUT,
        )
    except asyncio.TimeoutError:
        return None
    else:
        return result


class MetadataFetcher:
    def __init__(
        self, on_metadata_result: Optional[Callable[[bytes, bytes], None]] = None
    ):
        self._active_workers: Dict[bytes, asyncio.Future] = dict()

        self.on_metadata_result = on_metadata_result

    def _on_parent_task_done(self, info_hash: bytes, task: asyncio.Future):
        del self._active_workers[info_hash]
        try:
            metadata = task.result()
            if not metadata:
                return
        except asyncio.CancelledError:
            return

        if self.on_metadata_result:
            self.on_metadata_result(info_hash, metadata)

    def _on_child_task_done(
        self, parent_task: asyncio.Future, child_task: asyncio.Future
    ):
        parent_task.child_count -= 1  # type: ignore
        try:
            metadata = child_task.result()
            if metadata and not parent_task.done():
                parent_task.set_result(metadata)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logging.debug("Child task resulted in exception")
            logger.exception(e)

        if parent_task.child_count <= 0 and not parent_task.done():  # type: ignore
            parent_task.set_result(None)

    def fetch(
        self,
        info_hash: bytes,
        peer_address: PeerAddress,
        max_metadata_size: int = 10_000_000,
    ):
        event_loop = asyncio.get_event_loop()

        if info_hash not in self._active_workers:
            parent_future = event_loop.create_future()
            parent_future.child_count = 0  # type: ignore
            parent_future.add_done_callback(
                lambda f: self._on_parent_task_done(info_hash, f)
            )
            self._active_workers[info_hash] = parent_future

        parent_future = self._active_workers[info_hash]

        if parent_future.done():
            return

        if (
            parent_future.child_count  # type: ignore
            >= CRAWLER_METADATA_MAX_SIMULTANEOUS_WORKERS_PER_INFO_HASH
        ):
            return

        task = asyncio.ensure_future(
            fetch_metadata(
                info_hash=info_hash,
                peer_address=peer_address,
                max_metadata_size=max_metadata_size,
            )
        )
        task.add_done_callback(lambda t: self._on_child_task_done(parent_future, t))

        parent_future.child_count += 1  # type: ignore
        parent_future.add_done_callback(lambda f: task.cancel())
