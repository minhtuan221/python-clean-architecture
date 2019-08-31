from flask import Flask
from app.domain.usecase.user import UserService
from app.domain.usecase.user_role import UserRoleService
from app.infrastructure.persistence.user import UserRepository
from app.infrastructure.persistence.role import RoleRepository
from app.config import cli_config
from app.cmd.center_store import CenterStore
from app.domain.usecase.middleware import Middleware

print('cli_config.__dict__', cli_config.__dict__)

center_store = CenterStore(cli_config)

user_repository = UserRepository(center_store.connection_pool)
role_repository = RoleRepository(center_store.connection_pool)

user_service = UserService(
    user_repository, cli_config.PUBLIC_KEY, secret_key=cli_config.PRIVATE_KEY)

user_role_service = UserRoleService(role_repository, user_repository)

middleware = Middleware(user_service)


def create_app(config_object):
    app: Flask = Flask(__name__)
    app.config.from_object(config_object)

    from app.infrastructure.http.user import user_controller

    app.register_blueprint(user_controller)
    return app


app = create_app(cli_config)
