from peewee import Model, PostgresqlDatabase

from stilio.config import (
    DATABASE_HOST,
    DATABASE_NAME,
    DATABASE_PASSWORD,
    DATABASE_PORT,
    DATABASE_USER,
)

db = PostgresqlDatabase(
    DATABASE_NAME,
    host=DATABASE_HOST,
    port=DATABASE_PORT,
    user=DATABASE_USER,
    password=DATABASE_PASSWORD,
    autorollback=True,
)


class BaseModel(Model):
    class Meta:
        database = db


@db.connection_context()
def init() -> None:
    from stilio.persistence.constants import MODELS

    db.create_tables(MODELS)
