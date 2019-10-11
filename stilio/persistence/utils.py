import datetime
from logging import Logger
from sqlite3 import IntegrityError
from typing import List, Tuple

import sqlalchemy

from stilio.persistence.exceptions import StoringError
from stilio.persistence.torrents import Torrent, File, metadata, database


def init() -> None:
    engine = sqlalchemy.create_engine(str(database.url))
    metadata.create_all(engine)


async def store_metadata(
    info_hash: bytes, metadata: dict, logger: Logger = None
) -> None:
    name = metadata[b"name"].decode("utf-8")

    files: List[dict] = []
    if b"files" in metadata:
        for file in metadata[b"files"]:
            if any(b"/" in item for item in file[b"path"]):
                raise StoringError(message="Path contains trailing slashes")
            path = "/".join(i.decode("utf-8") for i in file[b"path"])
            files.append({"path": path, "size": file[b"length"]})
    else:
        files.append({"path": name, "size": metadata[b"length"]})

    try:
        torrent = await Torrent.objects.create(
            info_hash=info_hash.hex(), name=name, date=datetime.datetime.now()
        )
    except IntegrityError:
        pass
    else:
        for file in files:
            await File.objects.create(
                path=file["path"], size=file["size"], torrent=torrent
            )

    if logger:
        logger.info(f"Added: {name}")
