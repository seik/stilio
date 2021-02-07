from contextvars import ContextVar

import peewee
from peewee import Model, PostgresqlDatabase

from stilio.config import (
    DATABASE_HOST,
    DATABASE_NAME,
    DATABASE_PASSWORD,
    DATABASE_PORT,
    DATABASE_USER,
)

db_state_default = {"closed": None, "conn": None, "ctx": None, "transactions": None}
db_state = ContextVar("db_state", default=db_state_default.copy())


class PeeweeConnectionState(peewee._ConnectionState):
    def __init__(self, **kwargs):
        super().__setattr__("_state", db_state)
        super().__init__(**kwargs)

    def __setattr__(self, name, value):
        self._state.get()[name] = value

    def __getattr__(self, name):
        return self._state.get()[name]


db = PostgresqlDatabase(
    DATABASE_NAME,
    host=DATABASE_HOST,
    port=DATABASE_PORT,
    user=DATABASE_USER,
    password=DATABASE_PASSWORD,
    autorollback=True,
)
db._state = PeeweeConnectionState()


class BaseModel(Model):
    class Meta:
        database = db


@db.connection_context()
def init() -> None:
    from stilio.persistence.constants import MODELS

    db.connect()
    db.create_tables(MODELS)
    db.close()
