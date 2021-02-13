from uuid import uuid4

from faker import Faker
from playhouse.postgres_ext import fn

from stilio.persistence import database
from stilio.persistence.database import db
from stilio.persistence.torrents.models import Torrent


@db.connection_context()
def create_fake_data() -> None:
    fake = Faker()
    for _ in range(1_000):
        name = fake.text()[10:]
        torrent_id = Torrent.insert(
            info_hash=uuid4(),
            name=name,
            search_name=fn.to_tsvector(name),
            size="",
            files="",
        ).execute()
        print(f"Added torrent with ID {torrent_id} to the database")


if __name__ == "__main__":
    database.init()
    create_fake_data()
