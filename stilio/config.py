import logging

DATABASE_URL = "sqlite:///data/db.sqlite"

# Crawler config variables
# --------------------------------------------------------
CRAWLER_DEBUG_LEVEL = logging.DEBUG
CRAWLER_ADDRESS = "0.0.0.0"
CRAWLER_PORT = 6881
CRAWLER_BOOTSTRAP_NODES = [
    ("router.bittorrent.com", 6881),
    ("dht.transmissionbt.com", 6881),
    ("router.utorrent.com", 6881),
]
CRAWLER_METADATA_MAX_SIMULTANEOUS_WORKERS_PER_INFO_HASH = 3
CRAWLER_METADATA_FETCH_TIMEOUT = 100  # In seconds
