from typing import Optional


class PersistenceError(Exception):
    def __init__(self, message: str = None):
        self.message: Optional[str] = message


class StoringError(PersistenceError):
    pass
