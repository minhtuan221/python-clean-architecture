from app.domain.model.base import ConnectionPool
from functools import wraps


class CenterStore(object):
    def __init__(self, cli_config):
        self.config = cli_config
        self.connection_pool = ConnectionPool(cli_config.DATABASE_URL, echo=True)
        self.logger = None

