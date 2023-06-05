from flask import Blueprint, request, g

from app.cmd.center_store import user_role_service, user_service, middleware
from app.domain.model.user import User

user_controller = Blueprint('user_controller', __name__)

confirm_path = '/user/confirm/'
reset_password_path = '/user/reset_password/'


@user_controller.route('/users', methods=['POST'])
@middleware.error_handler
def sign_up():
    content: dict = request.get_json(silent=True)
    email = content.get('email', '')
    password = content.get('password', '')
    token = user_service.sign_up_new_user(email, password, confirm_url=request.url_root+confirm_path)
    return {'token': token}


@user_controller.route(confirm_path+'<token>', methods=['GET'])
@middleware.error_handler
def user_confirm_sign_up(token):
    confirm = user_service.confirm_user_email(token)
    if confirm:
        return {'message': 'User confirmed. Please login again'}
    return {'message': 'User confirmation failed'}


@user_controller.route('/user/reset_password', methods=['POST'])
@middleware.error_handler
def user_reset_password():
    content: dict = request.get_json(silent=True)
    email = content.get('email', '')
    user_service.request_reset_user_password(email, confirm_url=request.url_root+reset_password_path)
    return {'message': f'Confirmation link was sent to the email {email}'}


@user_controller.route(reset_password_path+'<token>', methods=['GET'])
@middleware.error_handler
def user_confirm_reset_password(token):
    confirm = user_service.confirm_reset_user_password(token)
    if confirm:
        return {'message': 'Password reset. Please check your email to receive new password'}
    return {'message': 'Reset password confirmation failed'}


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
    return {'message': r}
