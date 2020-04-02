from sanic import blueprints
from sanic.request import Request
import requests

from app.cmd.http import user_service, sanic_adapter_middleware as middleware

user_controller = blueprints.Blueprint(__name__)

confirm_path = '/user/confirm/'
reset_password_path = '/user/reset_password/'


@user_controller.route('/', methods=['GET'])
@middleware.error_handler
def welcome(request: Request):
    ex = requests.get("https://example.com/")
    return {"message": ex.text}

@user_controller.route('/users', methods=['POST'])
@middleware.error_handler
def sign_up(request: Request):
    content: dict = request.json
    email = content.get('email', '')
    password = content.get('password', '')
    token = user_service.sign_up_new_user(email, password, confirm_url=request.url_for('user_confirm_sign_up', token=''))
    return {'token': token}


@user_controller.route(confirm_path+'<token>', methods=['GET'])
@middleware.error_handler
def user_confirm_sign_up(request: Request, token):
    confirm = user_service.confirm_user_email(token)
    if confirm:
        return {'message': 'User confirmed. Please login again'}
    return {'message': 'User confirmation failed'}


@user_controller.route('/user/reset_password', methods=['POST'])
@middleware.error_handler
def user_reset_password(request: Request):
    content: dict = request.json
    email = content.get('email', '')
    user_service.request_reset_user_password(email, confirm_url=request.url_for('user_confirm_reset_password', token=''))
    return {'message': f'Confirmation link was sent to the email {email}'}


@user_controller.route(reset_password_path+'<token>', methods=['GET'])
@middleware.error_handler
def user_confirm_reset_password(request: Request, token):
    confirm = user_service.confirm_reset_user_password(token)
    if confirm:
        return {'message': 'Password reset. Please check your email to receive new password'}
    return {'message': 'Reset password confirmation failed'}


@user_controller.route('/login', methods=['POST'])
@middleware.error_handler
def login(request: Request):
    content: dict = request.json
    email = content.get('email', '')
    password = content.get('password', '')
    token = user_service.login(email, password)
    return {'token': token}


@user_controller.route('/users/profile', methods=['GET'])
@middleware.error_handler
@middleware.require_permissions()
def get_user_profile(request: Request):
    return {'user': request.headers['user'], 'roles': request.headers['roles'], 'permission': request.headers['permissions']}


@user_controller.route('/users/<id>/password', methods=['PUT'])
@middleware.error_handler
@middleware.require_permissions()
def update_password(request: Request, id):
    content: dict = request.json
    old_password = content.get('old_password', '')
    new_password = content.get('new_password', '')
    retype_password = content.get('retype_password', '')
    user = user_service.update_password(int(id), old_password, new_password, retype_password)
    return user.to_json()


@user_controller.route('/logout', methods=['GET'])
@middleware.error_handler
@middleware.require_permissions()
def logout(request: Request):
    r = user_service.logout(request.headers['auth_token'])
    return {'message': r}
