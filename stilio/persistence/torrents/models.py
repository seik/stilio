from __future__ import annotations

import datetime as dt
from typing import List

from peewee import (
    BigIntegerField,
    CharField,
    DateTimeField,
    ForeignKeyField,
    IntegerField,
    Tuple,
)

from stilio.persistence.database import BaseModel


class Torrent(BaseModel):
    info_hash = CharField(max_length=40, unique=True)
    name = CharField(max_length=512)

    seeders = IntegerField(default=0)
    leechers = IntegerField(default=0)

    last_update = DateTimeField(default=dt.datetime.now)
    last_update_change = DateTimeField(default=dt.datetime.now)

    added_at = DateTimeField(default=dt.datetime.now)

    @property
    def size(self) -> int:
        # TODO handle this with an aggregation
        return sum([file.size for file in self.files])

    def __str__(self):
        return self.name

    @classmethod
    def exists(cls, info_hash: bytes):
        return cls.select().where(cls.info_hash == info_hash.hex()).exists()

    @classmethod
    def total_torrent_count(cls) -> int:
        count = cls.select().count()
        return count

    @classmethod
    def search_by_name(
        cls, name: str, limit=None, offset=None
    ) -> Tuple[List["Torrent"], int]:
        queryset = cls.select().where(
            (Torrent.name.contains(name))
            | (Torrent.name.contains(name.replace(" ", ".")))
            | (Torrent.name.contains(name.replace(" ", "-")))
        )

        torrent_count = queryset.select().count()
        torrents = (
            queryset.select()
            .order_by(Torrent.added_at.desc())
            .limit(limit)
            .offset(offset)
            .execute()
        )

        return torrents, torrent_count


class File(BaseModel):
    torrent = ForeignKeyField(Torrent, backref="files")

    path = CharField(max_length=512)
    size = BigIntegerField()

    def __str__(self):
        return self.path
