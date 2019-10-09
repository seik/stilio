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

    @property
    def size(self):
        return 1


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
