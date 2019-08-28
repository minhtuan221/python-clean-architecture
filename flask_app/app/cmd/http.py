from flask import Flask

from app.domain.usecase.user import UserUsecase
from app.infrastructure.persistence.user import UserRepository
from app.config import cli_config
from app.cmd.center_store import CenterStore


print('cli_config.__dict__', cli_config.__dict__)

center_store = CenterStore(cli_config)

user_repository = UserRepository(center_store.connection_pool)
user_usecase = UserUsecase(user_repository)


def create_app(config_object):
    app: Flask = Flask(__name__)
    app.config.from_object(config_object)

    from app.infrastructure.http.user import user_controller

    app.register_blueprint(user_controller)
    return app


app = create_app(cli_config)
