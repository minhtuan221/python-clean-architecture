from typing import List

from fastapi import APIRouter, Request

from app.cmd.http import user_service, fastapi_middleware as middleware, user_role_service
from app.pkgs import errors as ec
from .api_model import LoginReq, UserAPI, UserConfirm, RoleAPI, User2PermissionAPI

record_not_found = ec.record_not_found

fastapi_admin = APIRouter()


@fastapi_admin.post("/admin", tags=["admin"], response_model=UserAPI)
@middleware.error_handler
@middleware.require_permissions('admin', 'admin.create')
async def create_new_user_by_admin(request: Request, e: LoginReq):
    user = user_service.create_new_user(e.email, e.password)
    return user.to_json()


@fastapi_admin.get('/admin/users', tags=["admin"], response_model=List[UserAPI])
@middleware.error_handler
@middleware.require_permissions('admin')
async def find_all(request: Request, search_word: str = '', page: int = 1):
    users = user_service.search(search_word, page=int(page))
    res = []
    for u in users:
        res.append(u.to_json())
    return res


@fastapi_admin.get('/admin/users/{_id}', tags=["admin"], response_model=UserAPI)
@middleware.error_handler
@middleware.require_permissions('admin')
async def find_one(request: Request, _id: str):
    user = user_service.find_by_id(int(_id))
    if user:
        return user.to_json()
    raise record_not_found


@fastapi_admin.get('/admin/users/{_id}/profile', tags=["admin"], response_model=UserAPI)
@middleware.error_handler
@middleware.require_permissions('admin')
async def find_one_with_all_profile(request: Request, _id: str):
    user, permissions = user_service.find_all_user_info_by_id(int(_id))
    if user:
        user_dict = user.to_json()
        user_dict['permissions'] = [p.to_json() for p in permissions]
        return user_dict
    raise record_not_found


@fastapi_admin.put('/admin/users/{_id}/confirm', tags=["admin"], response_model=UserAPI)
@middleware.error_handler
@middleware.require_permissions('admin', 'admin.update')
async def update_is_confirmed(request: Request, _id: str, u: UserConfirm):
    is_confirmed = u.is_confirmed
    user = user_service.update_is_confirmed(int(_id), is_confirmed)
    return user.to_json()


# admin role-permission base access control
@fastapi_admin.post('/admin/roles', tags=["admin"], response_model=RoleAPI)
@middleware.error_handler
@middleware.require_permissions('admin', 'admin.create')
async def create_new_role(request: Request, u: RoleAPI):
    name = u.name
    description = u.description
    role = user_role_service.create_new_role(name, description)
    return role.to_json()


@fastapi_admin.get('/admin/roles', tags=["admin"], response_model=List[RoleAPI])
@middleware.error_handler
@middleware.require_permissions('admin')
async def view_role(request: Request, name: str, page: int):
    roles_dict = []
    roles = user_role_service.search_roles_with_permission(name, page=int(page))
    for r in roles:
        roles_dict.append(r.to_json())
    return roles_dict


@fastapi_admin.get('/admin/roles/{role_id}', tags=["admin"], response_model=List[RoleAPI])
@middleware.error_handler
@middleware.require_permissions('admin')
async def view_role_by_admin(request: Request, role_id: str):
    role = user_role_service.find_by_id(int(role_id))
    return role.to_json()


@fastapi_admin.post('/admin/users2roles', tags=["admin"], response_model=UserAPI)
@middleware.error_handler
@middleware.require_permissions('admin', 'admin.update')
async def append_role_to_user_by_admin(request: Request, u: User2PermissionAPI):
    user_id = u.user_id
    role_id = u.role_id
    user = user_role_service.append_role_to_user(user_id, role_id)
    return user.to_json()


@fastapi_admin.put('/admin/users2roles', tags=["admin"], response_model=UserAPI)
@middleware.error_handler
@middleware.require_permissions('admin', 'admin.update')
async def remove_role_to_user_by_admin(request: Request, u: User2PermissionAPI):
    user_id = u.user_id
    role_id = u.role_id
    u = user_role_service.remove_role_to_user(user_id, role_id)
    return u.to_json()


# permission append, remove...
@fastapi_admin.get('/admin/permissions', tags=["admin"], response_model=List[str])
@middleware.error_handler
@middleware.require_permissions('admin')
async def view_all_available_permission_by_admin(request: Request):
    p_list = list(middleware.permissions_list)
    return p_list


@fastapi_admin.post('/admin/roles2permissions', tags=["admin"], response_model=RoleAPI)
@middleware.error_handler
@middleware.require_permissions('admin', 'admin.update')
async def append_permission_to_role_by_admin(request: Request, u: User2PermissionAPI):
    role_id = u.role_id
    permission = u.permission
    r = user_role_service.append_permission_to_role(role_id, permission)
    return r.to_json()


@fastapi_admin.put('/admin/roles2permissions', tags=["admin"], response_model=RoleAPI)
@middleware.error_handler
@middleware.require_permissions('admin', 'admin.update')
async def remove_permission_to_role_by_admin(request: Request, u: User2PermissionAPI):
    role_id = u.role_id
    permission = u.permission
    r = user_role_service.remove_permission_to_role(role_id, permission)
    return r.to_json()
