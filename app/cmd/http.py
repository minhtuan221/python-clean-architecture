from flask import Flask
from app.domain.usecase.user import UserService
from app.domain.usecase.user_role import UserRoleService
from app.infrastructure.persistence.user import UserRepository
from app.infrastructure.persistence.role import RoleRepository
from app.infrastructure.persistence.access_policy import AccessPolicyRepository
from app.infrastructure.persistence.blacklist_token import BlacklistTokenRepository
from app.config import cli_config
from app.cmd.center_store import CenterStore
from app.domain.usecase.middleware import Middleware

# print('cli_config.__dict__', cli_config.__dict__)

center_store = CenterStore(cli_config)

user_repository = UserRepository(center_store.connection_pool)
role_repository = RoleRepository(center_store.connection_pool)
access_policy_repository = AccessPolicyRepository(center_store.connection_pool)
blacklist_token_repository = BlacklistTokenRepository(center_store.connection_pool)

user_role_service = UserRoleService(role_repository, user_repository, access_policy_repository)

user_service = UserService(
    user_repository, access_policy_repository, blacklist_token_repository, cli_config.PUBLIC_KEY, secret_key=cli_config.PRIVATE_KEY)

middleware = Middleware(user_service)


def create_app(config_object):
    app: Flask = Flask(__name__)
    app.config.from_object(config_object)

    from app.infrastructure.http.user import user_controller
    from app.infrastructure.http.admin import  admin_controller

    app.register_blueprint(user_controller)
    app.register_blueprint(admin_controller)

    return app


app = create_app(cli_config)
