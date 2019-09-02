from flask import Blueprint, request, g

from app.cmd.http import user_service, middleware, user_role_service
from app.domain.model.user import User

user_controller = Blueprint('user_controller', __name__)


@user_controller.route('/users', methods=['POST'])
@middleware.error_handler
def sign_up():
    content: dict = request.get_json(silent=True)
    email = content.get('email', '')
    password = content.get('password', '')
    token = user_service.sign_up_new_user(email, password)
    return {'token': token}


@user_controller.route('/login', methods=['POST'])
@middleware.error_handler
def login():
    content: dict = request.get_json(silent=True)
    email = content.get('email', '')
    password = content.get('password', '')
    token = user_service.login(email, password)
    return {'token': token}


@user_controller.route('/users/profile', methods=['GET'])
@middleware.error_handler
@middleware.verify_auth_token
def get_user_profile():
    return {'user': g.user, 'roles': g.roles, 'permission': g.permissions}


@user_controller.route('/users/<id>/password', methods=['PUT'])
@middleware.error_handler
@middleware.verify_auth_token
def update_password(id):
    content: dict = request.get_json(silent=True)
    old_password = content.get('old_password', '')
    new_password = content.get('new_password', '')
    retype_password = content.get('retype_password', '')
    user = user_service.update_password(int(id), old_password, new_password, retype_password)
    return user.to_json()


@user_controller.route('/logout', methods=['GET'])
@middleware.error_handler
@middleware.verify_auth_token
def logout():
    r = user_service.logout(g.auth_token)
    return {'response': r}
