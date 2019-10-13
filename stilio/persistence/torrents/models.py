from __future__ import annotations

from typing import List

from peewee import IntegerField, CharField, DateTimeField, Tuple, ForeignKeyField

from stilio.persistence.database import BaseModel
import datetime as dt


class Torrent(BaseModel):
    info_hash = CharField(max_length=40, unique=True)
    name = CharField(max_length=512)
    added_at = DateTimeField(default=dt.datetime.now)

    @property
    def size(self) -> int:
        # TODO handle this with an aggregation
        return sum([file.size for file in self.files])

    def __str__(self):
        return self.name

    @staticmethod
    def total_torrent_count() -> int:
        count = Torrent.select().count()
        return count

    @staticmethod
    def search_by_name(
        name: str, limit=None, offset=None
    ) -> Tuple[List["Torrent"], int]:
        # TODO implement postgresql full search
        queryset = Torrent.select().where(Torrent.name.contains(name))

        torrent_count = queryset.select().count()
        torrents = queryset.select().limit(limit).offset(offset).execute()

        return torrents, torrent_count


class File(BaseModel):
    torrent = ForeignKeyField(Torrent, backref="files")

    path = CharField(max_length=512)
    size = IntegerField()

    def __str__(self):
        return self.path
