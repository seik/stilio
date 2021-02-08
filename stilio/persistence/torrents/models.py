from __future__ import annotations

import datetime as dt
from typing import List, Tuple

from peewee import (
    BigIntegerField,
    CharField,
    DateTimeField,
    ForeignKeyField,
    IntegerField,
)
from playhouse.postgres_ext import Match, TSVectorField

from stilio.persistence.database import BaseModel


class Torrent(BaseModel):
    info_hash = CharField(max_length=40, unique=True)
    name = CharField(max_length=512)
    search_name = TSVectorField()

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
        # Remove characters that are not considered a "letter"
        cleaned_name = "".join([letter for letter in name if letter.isalpha() or " "])
        # Every word is required so &
        cleaned_name = cleaned_name.replace(" ", " & ")
        queryset = cls.select().where(Torrent.search_name.match(cleaned_name))

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
