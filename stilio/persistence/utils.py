from typing import List

from peewee import IntegrityError

from stilio.persistence.exceptions import StoringError
from stilio.persistence.torrents.models import File, Torrent


def store_metadata(info_hash: bytes, metadata: dict, logger=None) -> None:
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
        torrent = Torrent.insert(info_hash=info_hash.hex(), name=name).execute()
    except IntegrityError as e:
        logger.exception(e)
        return
    else:
        for file in files:
            File.insert(path=file["path"], size=file["size"], torrent=torrent).execute()

    if logger:
        logger.info(f"Added: {name}")
