from flask import Flask
from app.domain.usecase.user import UserUsecase
from app.infrastructure.persistence.user import UserRepository
from app.config import cli_config
from app.cmd.center_store import CenterStore
from app.domain.usecase.middleware import Middleware

print('cli_config.__dict__', cli_config.__dict__)

center_store = CenterStore(cli_config)

user_repository = UserRepository(center_store.connection_pool)

user_usecase = UserUsecase(
    user_repository, cli_config.PUBLIC_KEY, secret_key=cli_config.PRIVATE_KEY)
middleware = Middleware(user_usecase)


def create_app(config_object):
    app: Flask = Flask(__name__)
    app.config.from_object(config_object)

    from app.infrastructure.http.user import user_controller

    app.register_blueprint(user_controller)
    return app


app = create_app(cli_config)
