from app.domain.model import ConnectionPool
from app.domain.usecase.user import UserService
from app.domain.usecase.user_role import UserRoleService
from app.infrastructure.http.fastapi_adapter.middle_ware import FastAPIMiddleware
from app.infrastructure.http.flask_adapter.middleware import Middleware
from app.infrastructure.http.sanic_adapter import middleware as sanic_utils
from app.infrastructure.persistence.access_policy import AccessPolicyRepository
from app.infrastructure.persistence.blacklist_token import BlacklistTokenRepository
from app.infrastructure.persistence.role import RoleRepository
from app.infrastructure.persistence.user import UserRepository
from app.pkgs.injector import Container
from app.pkgs.logger import set_gunicorn_custom_logger
from logging import Logger
from app.config import cli_config


container = Container()
container.add_instance(cli_config)

connection_pool = container.add_instance(ConnectionPool(cli_config.DATABASE_URL, echo=cli_config.SQL_ECHO))
access_logger, error_logger = set_gunicorn_custom_logger(path=cli_config.LOG_FOLDER)
# access_logger, error_logger = Logger('access'), Logger('error')
access_logger: Logger = access_logger
error_logger: Logger = error_logger
connection_pool = container.add_instance(error_logger)

# all container should be placed here
container.add_singleton(UserRepository)
container.add_singleton(RoleRepository)
container.add_singleton(AccessPolicyRepository)
container.add_singleton(BlacklistTokenRepository)
container.add_singleton(UserRoleService)
container.add_singleton(UserService)
container.add_singleton(Middleware)
container.build()

user_role_service = container.get_singleton(UserRoleService)
user_service = container.get_singleton(UserService)
middleware = Middleware(user_service, error_logger)
sanic_adapter_middleware = sanic_utils.Middleware(user_service, error_logger)
fastapi_middleware = FastAPIMiddleware(user_service, None)
