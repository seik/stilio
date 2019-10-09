class MetadataFetcherException(Exception):
    def __init__(self, message: str):
        self.message = message


class InvalidHandshake(MetadataFetcherException):
    pass


class InvalidMetadata(MetadataFetcherException):
    pass
