from logging import Logger

from app.config import cli_config
from app.domain.model import ConnectionPool
from app.domain.service.group_service import GroupService
from app.domain.service.process_maker.action_service import ActionService
from app.domain.service.process_maker.activity_service import ActivityService
from app.domain.service.process_maker.process_service import ProcessService
from app.domain.service.process_maker.target_service import TargetService
from app.domain.service.process_maker.request_service import RequestService
from app.domain.service.user import UserService
from app.domain.service.user_role import UserRoleService
from app.infrastructure.http.fastapi_adapter.middle_ware import FastAPIMiddleware
from app.infrastructure.http.flask_adapter.middleware import Middleware
from app.infrastructure.http.sanic_adapter import middleware as sanic_utils
from app.infrastructure.persistence.access_policy import AccessPolicyRepository
from app.infrastructure.persistence.blacklist_token import BlacklistTokenRepository
from app.infrastructure.persistence.group import GroupRepository
from app.infrastructure.persistence.process_maker.action import ActionRepository
from app.infrastructure.persistence.process_maker.activity import ActivityRepository
from app.infrastructure.persistence.process_maker.process import ProcessRepository
from app.infrastructure.persistence.process_maker.request import RequestRepository
from app.infrastructure.persistence.process_maker.request_stakeholder import \
    RequestStakeholderRepository
from app.infrastructure.persistence.process_maker.route import RouteRepository
from app.infrastructure.persistence.process_maker.state import StateRepository
from app.infrastructure.persistence.process_maker.target import TargetRepository
from app.infrastructure.persistence.process_maker.request_action import RequestActionRepository
from app.infrastructure.persistence.process_maker.request_data import RequestDataRepository
from app.infrastructure.persistence.process_maker.request_note import RequestNoteRepository
from app.infrastructure.persistence.role import RoleRepository
from app.infrastructure.persistence.user import UserRepository
from app.pkgs.injector import Container
from app.pkgs.logger import set_gunicorn_custom_logger

container = Container()
container.add_instance(cli_config)

connection_pool = container.add_instance(
    ConnectionPool(cli_config.DATABASE_URL, echo=cli_config.SQL_ECHO)
)
access_logger, error_logger = set_gunicorn_custom_logger(path=cli_config.LOG_FOLDER)
# access_logger, error_logger = Logger('access'), Logger('error')
access_logger: Logger = access_logger
error_logger: Logger = error_logger
container.add_instance(error_logger)

# all container should be placed here
container.add_singleton(UserRepository)
container.add_singleton(RoleRepository)
container.add_singleton(AccessPolicyRepository)
container.add_singleton(BlacklistTokenRepository)
container.add_singleton(UserRoleService)
container.add_singleton(GroupRepository)
container.add_singleton(UserService)
container.add_singleton(Middleware)
container.add_singleton(FastAPIMiddleware)
container.add_singleton(ProcessRepository)
container.add_singleton(ActivityRepository)
container.add_singleton(ActionRepository)
container.add_singleton(TargetRepository)
container.add_singleton(RequestRepository)
container.add_singleton(RequestDataRepository)
container.add_singleton(RequestNoteRepository)
container.add_singleton(RequestActionRepository)
container.add_singleton(RequestStakeholderRepository)
container.add_singleton(RouteRepository)
container.add_singleton(StateRepository)
container.add_singleton(ProcessService)
container.add_singleton(ActionService)
container.add_singleton(ActivityService)
container.add_singleton(TargetService)
container.add_singleton(GroupService)
container.add_singleton(RequestService)
container.build()

user_role_service = container.get_singleton(UserRoleService)
user_service = container.get_singleton(UserService)

middleware = Middleware(user_service, error_logger)
sanic_adapter_middleware = sanic_utils.Middleware(user_service, error_logger)
fastapi_middleware = container.get_singleton(FastAPIMiddleware)
