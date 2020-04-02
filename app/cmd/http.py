from flask import Flask
from sanic import Sanic
from sanic_cors import CORS

from app.cmd.center_store import CenterStore
from app.config import cli_config
from app.domain.usecase.user import UserService
from app.domain.usecase.user_role import UserRoleService
from app.infrastructure.http.flask_adapter.middleware import Middleware, set_logger
from app.infrastructure.http.sanic_adapter import middleware as sanic_utils
from app.infrastructure.http.sanic_adapter.compress import Compress
from app.infrastructure.persistence.access_policy import AccessPolicyRepository
from app.infrastructure.persistence.blacklist_token import BlacklistTokenRepository
from app.infrastructure.persistence.role import RoleRepository
from app.infrastructure.persistence.user import UserRepository

# print('cli_config.__dict__', cli_config.__dict__)

center_store = CenterStore(cli_config)

user_repository = UserRepository(center_store.connection_pool)
role_repository = RoleRepository(center_store.connection_pool)
access_policy_repository = AccessPolicyRepository(center_store.connection_pool)
blacklist_token_repository = BlacklistTokenRepository(center_store.connection_pool)

user_role_service = UserRoleService(role_repository, user_repository, access_policy_repository)

user_service = UserService(
    user_repository, access_policy_repository, blacklist_token_repository, cli_config.PUBLIC_KEY,
    secret_key=cli_config.PRIVATE_KEY)

middleware = Middleware(user_service, center_store.error_logger)
sanic_adapter_middleware = sanic_utils.Middleware(user_service, center_store.error_logger)


def create_first_time_config(admin_email, admin_password):
    admin = user_service.user_repo.find_by_email(admin_email)
    if not admin:
        admin = user_service.create_new_user(admin_email, admin_password)

    admin_role = user_role_service.role_repo.find_by_name('admin')
    if not admin_role:
        admin_role = user_role_service.create_new_role('admin', 'Admin role with super power')

    try:
        user_role_service.append_permission_to_role(admin_role.id, 'admin')
    except Exception as e:
        print('append_permission_to_role got error:', e)
    try:
        user_role_service.append_role_to_user(admin.id, admin_role.id)
    except Exception as e:
        print('append_role_to_user got error:', e)


def create_flask_app(config_object):
    flask_app: Flask = Flask(__name__)
    flask_app.config.from_object(config_object)

    from app.infrastructure.http.flask_adapter.user import user_controller
    from app.infrastructure.http.flask_adapter.admin import admin_controller

    flask_app.register_blueprint(user_controller)
    flask_app.register_blueprint(admin_controller)

    set_logger(center_store.access_logger, flask_app)

    return flask_app


def create_sanic_app(config_object):
    sanic_app: Sanic = Sanic(__name__)
    sanic_app.config.from_object(config_object)
    # Compress(sanic_app)
    # CORS(sanic_app, automatic_options=True)

    from app.infrastructure.http.sanic_adapter.user import user_controller
    from app.infrastructure.http.sanic_adapter.admin import admin_controller

    sanic_app.blueprint(user_controller)
    sanic_app.blueprint(admin_controller)

    if not config_object.DEBUG:
        sanic_utils.set_logger(center_store.access_logger, sanic_app)
        sanic_app.debug = False
        sanic_app.config.ACCESS_LOG = None

    return sanic_app


app = create_sanic_app(cli_config)
