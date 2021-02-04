from random import randint
from uuid import uuid4

from faker import Faker

from stilio.persistence import database
from stilio.persistence.database import db
from stilio.persistence.torrents.models import File, Torrent


@db.connection_context()
def create_fake_data() -> None:
    fake = Faker()
    for i in range(1_000):
        torrent_id = Torrent.insert(info_hash=uuid4(), name=fake.text()[10:]).execute()
        for j in range(randint(1, 10)):
            File.insert(
                path="path", size=randint(1, 10000), torrent=torrent_id
            ).execute()
        print(f"Added torrent with ID {torrent_id} to the database")


if __name__ == "__main__":
    database.init()
    create_fake_data()
