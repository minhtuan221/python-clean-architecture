from flask import Blueprint, request

from app.cmd.http import user_service, middleware, user_role_service
from app.domain.model.user import User

admin_controller = Blueprint('admin_controller', __name__)


@admin_controller.route('/admin/users', methods=['POST'])
@middleware.error_handler
@middleware.verify_auth_token
@middleware.require_permissions('admin')
def create_new_user_by_admin():
    content: dict = request.get_json(silent=True)
    email = content.get('email', '')
    password = content.get('password', '')
    user = user_service.create_new_user(email, password)
    return user.to_json()


@admin_controller.route('/admin/users', methods=['GET'])
@middleware.error_handler
@middleware.verify_auth_token
@middleware.require_permissions('admin')
def find_all():
    search_word = request.args.get('email', '')
    users = user_service.search(search_word)
    res = []
    for u in users:
        res.append(u.to_json())
    return res


@admin_controller.route('/admin/users/<id>')
@middleware.error_handler
@middleware.verify_auth_token
@middleware.require_permissions('admin')
def find_one(id):
    user: User = user_service.find_by_id(int(id))
    if user:
        return user.to_json()
    return {}


@admin_controller.route('/admin/users/<id>/profile')
@middleware.error_handler
@middleware.verify_auth_token
@middleware.require_permissions('admin')
def find_one_with_all_profile(id: int):
    user, permissions = user_service.find_all_user_info_by_id(int(id))
    if user:
        user_dict = user.to_json()
        user_dict['permissions'] = [p.to_json() for p in permissions]
        return user_dict
    return {}


@admin_controller.route('/admin/users/<id>/confirm', methods=['PUT'])
@middleware.error_handler
@middleware.verify_auth_token
@middleware.require_permissions('admin')
def update_is_confirmed(id):
    content: dict = request.get_json(silent=True)
    is_confirmed = content.get('is_confirmed', False)
    user = user_service.update_is_confirmed(int(id), is_confirmed)
    return user.to_json()

# admin role-permission base access control
@admin_controller.route('/admin/roles', methods=['POST'])
@middleware.error_handler
@middleware.verify_auth_token
@middleware.require_permissions('admin')
def create_new_role():
    content: dict = request.get_json(silent=True)
    name = content.get('name', '')
    description = content.get('description', '')
    role = user_role_service.create_new_role(name, description)
    return role.to_json()


@admin_controller.route('/admin/users/roles', methods=['POST'])
@middleware.error_handler
@middleware.verify_auth_token
@middleware.require_permissions('admin')
def append_role_to_user_by_admin():
    content: dict = request.get_json(silent=True)
    user_id = content.get('user_id', 0)
    role_id = content.get('role_id', 0)
    user = user_role_service.append_role_to_user(user_id, role_id)
    return user.to_json()


@admin_controller.route('/admin/users/roles', methods=['PUT'])
@middleware.error_handler
@middleware.verify_auth_token
@middleware.require_permissions('admin')
def remove_role_to_user_by_admin():
    content: dict = request.get_json(silent=True)
    user_id = content.get('user_id', 0)
    role_id = content.get('role_id', 0)
    u = user_role_service.remove_role_to_user(user_id, role_id)
    return u.to_json()


# permission append, remove...
@admin_controller.route('/admin/roles/permissions', methods=['POST'])
@middleware.error_handler
@middleware.verify_auth_token
@middleware.require_permissions('admin')
def append_permission_to_role_by_admin():
    content: dict = request.get_json(silent=True)
    role_id = content.get('role_id', 0)
    permission = content.get('permission', '')
    r = user_role_service.append_permission_to_role(role_id, permission)
    return r.to_json()


@admin_controller.route('/admin/permissions')
@middleware.error_handler
@middleware.verify_auth_token
@middleware.require_permissions('admin')
def view_all_available_permission_by_admin():
    return {'permission': list(middleware.permissions_list)}


@admin_controller.route('/admin/roles/<role_id>/permissions', methods=['GET'])
@middleware.error_handler
@middleware.verify_auth_token
@middleware.require_permissions('admin')
def view_permission_to_role_by_admin(role_id):
    permissions = user_role_service.view_permission_to_role(int(role_id))
    permissions_list = []
    for p in permissions:
        permissions_list.append(p.to_json())
    return permissions_list


@admin_controller.route('/admin/roles/permissions', methods=['PUT'])
@middleware.error_handler
@middleware.verify_auth_token
@middleware.require_permissions('admin')
def remove_permission_to_role_by_admin():
    content: dict = request.get_json(silent=True)
    user_id = content.get('user_id', 0)
    role_id = content.get('role_id', 0)
    r = user_role_service.remove_permission_to_role(user_id, role_id)
    return r.to_json()
