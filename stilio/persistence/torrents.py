import asyncio
from typing import Tuple, List

import databases
import orm
import sqlalchemy

from stilio.config import DATABASE_URL

database = databases.Database(DATABASE_URL)
metadata = sqlalchemy.MetaData()


class Torrent(orm.Model):
    __tablename__ = "torrent"
    __database__ = database
    __metadata__ = metadata

    id = orm.Integer(primary_key=True)

    info_hash = orm.String(max_length=40, unique=True, index=True)
    name = orm.String(max_length=512)
    date = orm.DateTime()

    def __str__(self):
        return self.name

    async def get_size(self) -> int:
        files = await File.objects.filter(torrent=self).all()
        return sum([file.size for file in files])

    @staticmethod
    async def total_torrent_count() -> int:
        count = await Torrent.objects.count()
        return count

    @staticmethod
    async def search_by_name(
            name: str,
            limit=None,
            offset=None
    ) -> Tuple[List["Torrent"], int]:
        queryset = Torrent.objects.filter(name__icontains=name)
        torrent_count = await queryset.count()
        torrents = await queryset.limit(limit).offset(offset).all()

        # TODO ORM is not powerful enough even to let me do a simple
        # aggregation... search for an alternative.

        # This shit is slow. Really slow and I don't want to write a
        # raw SQL query

        # Add size to torrent results
        torrent_results = []
        for torrent in torrents:
            torrent.size = await torrent.get_size()
            torrent_results.append(torrent)

        return torrent_results, torrent_count


class File(orm.Model):
    __tablename__ = "file"
    __database__ = database
    __metadata__ = metadata

    id = orm.Integer(primary_key=True)

    path = orm.String(max_length=512)
    size = orm.Integer()

    torrent = orm.ForeignKey(Torrent)

    def __str__(self):
        return self.path
