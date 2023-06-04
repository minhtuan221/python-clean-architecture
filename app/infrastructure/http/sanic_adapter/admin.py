from sanic.blueprints import Blueprint
from sanic.request import Request

from app.cmd.center_store import user_role_service, user_service, \
    sanic_adapter_middleware as middleware
from app.domain.model.user import User

admin_controller = Blueprint(__name__)


@admin_controller.route('/admin/users', methods=['POST'])
@middleware.error_handler
@middleware.require_permissions('admin', 'admin.create')
def create_new_user_by_admin(request: Request):
    content: dict = request.json
    email = content.get('email', '')
    password = content.get('password', '')
    user = user_service.create_new_user(email, password)
    return user.to_json()


@admin_controller.route('/admin/users', methods=['GET'])
@middleware.error_handler
@middleware.require_permissions('admin')
def find_all(request: Request):
    search_word = request.args.get('email', '')
    page = request.args.get('page', 1)
    users = user_service.search(search_word, page=int(page))
    res = []
    for u in users:
        res.append(u.to_json())
    return res


@admin_controller.route('/admin/users/<id>')
@middleware.error_handler
@middleware.require_permissions('admin')
def find_one(request: Request, id):
    user: User = user_service.find_by_id(int(id))
    if user:
        return user.to_json()
    return {}


@admin_controller.route('/admin/users/<id>/profile')
@middleware.error_handler
@middleware.require_permissions('admin')
def find_one_with_all_profile(request: Request, id: int):
    user, permissions = user_service.find_all_user_info_by_id(int(id))
    if user:
        user_dict = user.to_json()
        user_dict['permissions'] = [p.to_json() for p in permissions]
        return user_dict
    return {}


@admin_controller.route('/admin/users/<id>/confirm', methods=['PUT'])
@middleware.error_handler
@middleware.require_permissions('admin', 'admin.update')
def update_is_confirmed(request: Request, id):
    content: dict = request.json
    is_confirmed = content.get('is_confirmed', False)
    user = user_service.update_is_confirmed(int(id), is_confirmed)
    return user.to_json()


# admin role-permission base access control
@admin_controller.route('/admin/roles', methods=['POST'])
@middleware.error_handler
@middleware.require_permissions('admin', 'admin.create')
def create_new_role(request: Request):
    content: dict = request.json
    name = content.get('name', '')
    description = content.get('description', '')
    role = user_role_service.create_new_role(name, description)
    return role.to_json()


@admin_controller.route('/admin/roles', methods=['GET'])
@middleware.error_handler
@middleware.require_permissions('admin')
def view_role(request: Request):
    content: dict = request.args
    name = content.get('name', '')
    page = content.get('page', 1)
    roles_dict = []
    roles = user_role_service.search_roles_with_permission(name, page=int(page))
    for r in roles:
        roles_dict.append(r.to_json())
    return roles_dict


@admin_controller.route('/admin/users/roles', methods=['POST'])
@middleware.error_handler
@middleware.require_permissions('admin', 'admin.update')
def append_role_to_user_by_admin(request: Request):
    content: dict = request.json
    user_id = content.get('user_id', 0)
    role_id = content.get('role_id', 0)
    user = user_role_service.append_role_to_user(user_id, role_id)
    return user.to_json()


@admin_controller.route('/admin/users/roles', methods=['PUT'])
@middleware.error_handler
@middleware.require_permissions('admin', 'admin.update')
def remove_role_to_user_by_admin(request: Request):
    content: dict = request.json
    user_id = content.get('user_id', 0)
    role_id = content.get('role_id', 0)
    u = user_role_service.remove_role_from_user(user_id, role_id)
    return u.to_json()


# permission append, remove...
@admin_controller.route('/admin/roles/permissions', methods=['POST'])
@middleware.error_handler
@middleware.require_permissions('admin', 'admin.update')
def append_permission_to_role_by_admin(request: Request):
    content: dict = request.json
    role_id = content.get('role_id', 0)
    permission = content.get('permission', '')
    r = user_role_service.append_permission_to_role(role_id, permission)
    return r.to_json()


@admin_controller.route('/admin/permissions')
@middleware.error_handler
@middleware.require_permissions('admin')
def view_all_available_permission_by_admin(request: Request):
    p_list = list(middleware.permissions_list)
    return {'permission': [{'name': p, 'id': p} for p in p_list]}


@admin_controller.route('/admin/roles/<role_id>', methods=['GET'])
@middleware.error_handler
@middleware.require_permissions('admin')
def view_role_by_admin(request: Request, role_id):
    role = user_role_service.find_by_id(int(role_id))
    return role.to_json()


@admin_controller.route('/admin/roles/permissions', methods=['PUT'])
@middleware.error_handler
@middleware.require_permissions('admin', 'admin.update')
def remove_permission_to_role_by_admin(request: Request):
    content: dict = request.json
    role_id = content.get('role_id', 0)
    permission = content.get('permission', '')
    r = user_role_service.remove_permission_from_role(role_id, permission)
    return r.to_json()
