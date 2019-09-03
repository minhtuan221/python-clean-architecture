from app.domain.model import ConnectionPool
from app.pkgs.logger import create_timed_rotating_log
from logging import Logger
from app.config import Config


class CenterStore(object):

    def __init__(self, cli_config: Config):
        self.config = cli_config
        self.connection_pool = ConnectionPool(cli_config.DATABASE_URL, echo=True)
        self.logger: Logger = create_timed_rotating_log(cli_config.LOG_FOLDER)
