from flask import Blueprint, request

from app.cmd.http import user_usecase, middleware, user_role_service

user_controller = Blueprint('user_controller', __name__)


@user_controller.route('/users', methods=['POST'])
@middleware.error_handler
def sign_up():
    pass


@user_controller.route('/login', methods=['POST'])
@middleware.error_handler
def login():
    content: dict = request.get_json(silent=True)
    email = content.get('email', '')
    password = content.get('password', '')
    token = user_usecase.login(email, password)
    return {'token': token}


@user_controller.route('/admin/users', methods=['POST'])
@middleware.error_handler
def create_new_user_by_admin():
    content: dict = request.get_json(silent=True)
    email = content.get('email', '')
    password = content.get('password', '')
    user = user_usecase.create_new_user(email, password)
    return user


@user_controller.route('/admin/users', methods=['GET'])
@middleware.error_handler
@middleware.verify_auth_token
def find_all():
    search_word = request.args.get('email', '')
    users = user_usecase.search(search_word)
    return users


@user_controller.route('/admin/users/<id>')
@middleware.error_handler
@middleware.verify_auth_token
def find_one(id):
    user = user_usecase.find_by_id(id)
    if user:
        return user
    return None


@user_controller.route('/users/<id>/password', methods=['PUT'])
@middleware.error_handler
def update_password(id):
    content: dict = request.get_json(silent=True)
    old_password = content.get('old_password', '')
    new_password = content.get('new_password', '')
    retype_password = content.get('retype_password', '')
    return user_usecase.update_password(id, old_password, new_password, retype_password)


@user_controller.route('/users/<id>/confirm', methods=['PUT'])
@middleware.error_handler
@middleware.verify_auth_token
def update_is_confirmed(id):
    content: dict = request.get_json(silent=True)
    is_confirmed = content.get('is_confirmed', False)
    user = user_usecase.update_is_confirmed(int(id), is_confirmed)
    return user


@user_controller.route('/admin/roles', methods=['POST'])
@middleware.error_handler
@middleware.verify_auth_token
def create_new_role():
    content: dict = request.get_json(silent=True)
    name = content.get('name', '')
    description = content.get('description', '')
    return user_role_service.create_new_role(name, description)


@user_controller.route('/admin/users/roles', methods=['POST'])
@middleware.error_handler
@middleware.verify_auth_token
def append_role_to_user_by_admin():
    content: dict = request.get_json(silent=True)
    user_id = content.get('user_id', '')
    role_id = content.get('role_id', '')
    return user_role_service.append_role_to_user(user_id, role_id)


@user_controller.route('/admin/users/roles', methods=['PUT'])
@middleware.error_handler
@middleware.verify_auth_token
def remove_role_to_user_by_admin():
    content: dict = request.get_json(silent=True)
    user_id = content.get('user_id', '')
    role_id = content.get('role_id', '')
    return user_role_service.remove_role_to_user(user_id, role_id)


@user_controller.route('/admin/roles/permissions', methods=['POST'])
@middleware.error_handler
@middleware.verify_auth_token
def append_permission_to_role_by_admin():
    content: dict = request.get_json(silent=True)
    role_id = content.get('role_id', '')
    permission = content.get('permission', '')
    return user_role_service.append_permission_to_role(role_id, permission)


@user_controller.route('/admin/roles/<role_id>/permissions', methods=['GET'])
@middleware.error_handler
@middleware.verify_auth_token
def view_permission_to_role_by_admin(role_id):
    return user_role_service.view_permission_to_role(int(role_id))


@user_controller.route('/admin/users/<user_id>/permissions', methods=['GET'])
@middleware.error_handler
@middleware.verify_auth_token
def view_permission_to_user_by_admin(user_id):
    return user_role_service.view_permission_to_user(int(user_id))


@user_controller.route('/admin/roles/permissions', methods=['PUT'])
@middleware.error_handler
@middleware.verify_auth_token
def remove_permission_to_role_by_admin():
    content: dict = request.get_json(silent=True)
    user_id = content.get('user_id', '')
    role_id = content.get('role_id', '')
    return user_role_service.remove_permission_to_role(user_id, role_id)


@user_controller.route('/users/<id>', methods=['DELETE'])
@middleware.error_handler
def delete(id):
    pass
