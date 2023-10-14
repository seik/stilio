import json

from peewee import IntegrityError
from playhouse.postgres_ext import fn

from stilio.persistence.exceptions import StoringError
from stilio.persistence.torrents.models import Torrent


class FileSystem:
    def __init__(self, file_path=None, root=False):
        self.children = []

        if file_path != None and not root:
            try:
                self.name, child = file_path.split("/", 1)
                self.children.append(FileSystem(child))
            except ValueError:
                self.name = file_path
        else:
            self.name = "/"

    def add_child(self, file_path):
        try:
            first_level, next_level = file_path.split("/", 1)
        except ValueError:
            # only one result, final file in path, add it
            self.children.append(FileSystem(file_path))
        else:
            # search for child and add the rest
            for child in self.children:
                if first_level == child.name:
                    child.add_child(next_level)
                    return
            else:
                # rest of the path not present in filesystem, add it
                self.children.append(FileSystem(file_path))

    def is_children(self, name: str) -> bool:
        return any(name == children.name for children in self.children)

    def make_dict(self):
        if len(self.children) > 0:
            dictionary = {self.name: []}
            for child in self.children:
                dictionary[self.name].append(child.make_dict())
            return dictionary
        else:
            return self.name


def store_metadata(info_hash: bytes, metadata: dict, logger=None) -> None:
    name = metadata[b"name"].decode("utf-8")
    search_name = name.replace(".", " ")
    files = get_file_structure(metadata, name)
    size = get_size(metadata)

    try:
        Torrent.insert(
            info_hash=info_hash.hex(),
            name=name,
            search_name=fn.to_tsvector(search_name),
            files=json.dumps(files, ensure_ascii=False),
            size=size,
        ).execute()
    except IntegrityError as e:
        logger.exception(e)
        return

    if logger:
        logger.info(f"Added: {name}")


def get_file_structure(metadata: dict, name: str) -> dict:
    files = FileSystem(root=True)

    if b"files" in metadata:
        for file in metadata[b"files"]:
            if any(b"/" in item for item in file[b"path"]):
                raise StoringError(message="Path contains trailing slashes")
            path = "/".join(i.decode("utf-8") for i in file[b"path"])
            files.add_child(path)
    else:
        files.add_child(name)

    return files.make_dict()


def get_size(metadata: dict) -> int:
    if b"files" in metadata:
        return sum([element[b"length"] for element in metadata[b"files"]])
    else:
        return 0
