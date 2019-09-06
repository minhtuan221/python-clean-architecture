from app.domain.model import ConnectionPool
from app.pkgs.logger import set_gunicorn_custom_logger
from logging import Logger
from app.config import Config


class CenterStore(object):

    def __init__(self, cli_config: Config):
        self.config = cli_config
        self.connection_pool = ConnectionPool(cli_config.DATABASE_URL, echo=False)
        access_logger, error_logger = set_gunicorn_custom_logger(path=cli_config.LOG_FOLDER)
        # access_logger, error_logger = Logger('access'), Logger('error')
        self.access_logger: Logger = access_logger
        self.error_logger: Logger = error_logger
