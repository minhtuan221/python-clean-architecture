from flask import Flask
from sanic import Sanic
from fastapi import FastAPI

from app.cmd.center_store import user_role_service, user_service


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

    # set_logger(center_store.access_logger, flask_app)

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
        # sanic_utils.set_logger(center_store.access_logger, sanic_app)
        sanic_app.debug = False
        sanic_app.config.ACCESS_LOG = None

    return sanic_app


def create_fastapi_app():
    fast_app = FastAPI(docs_url='/spec/api')

    from app.infrastructure.http.fastapi_adapter.admin import admin_api
    from app.infrastructure.http.fastapi_adapter.user import user_api
    from app.infrastructure.http.fastapi_adapter.process_maker.process import process_api
    from app.infrastructure.http.fastapi_adapter.process_maker.action import action_api
    from app.infrastructure.http.fastapi_adapter.process_maker.activity import activity_api
    from app.infrastructure.http.fastapi_adapter.process_maker.target import target_api
    from app.infrastructure.http.fastapi_adapter.group import group_api

    fast_app.include_router(admin_api, prefix='/api')
    fast_app.include_router(user_api, prefix='/api')
    fast_app.include_router(process_api, prefix='/api')
    fast_app.include_router(action_api, prefix='/api')
    fast_app.include_router(activity_api, prefix='/api')
    fast_app.include_router(group_api, prefix='/api')
    fast_app.include_router(target_api, prefix='/api')
    return fast_app


app = create_fastapi_app()
