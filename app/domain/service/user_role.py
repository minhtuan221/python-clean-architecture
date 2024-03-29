from typing import List

from app.domain.utils import error_collection
from app.domain.utils import validation
from app.domain.model.role import PermissionPolicy
from app.domain.model.user import Role
from app.infrastructure.persistence.access_policy import AccessPolicyRepository
from app.infrastructure.persistence.role import RoleRepository
from app.infrastructure.persistence.user import UserRepository
from app.pkgs import errors
from app.pkgs.query import get_start_stop_pos


class UserRoleService(object):

    def __init__(self, role_repo: RoleRepository, user_repo: UserRepository,
                 access_policy_repo: AccessPolicyRepository):
        self.role_repo = role_repo
        self.user_repo = user_repo
        self.access_policy_repo = access_policy_repo

    def create_new_role(self, name: str, description: str):
        name = name.lower()
        description = description.lower()
        validation.validate_name_without_space(name)
        role = Role(name=name, description=description)
        r = self.role_repo.find_by_name(name)
        if r:
            raise error_collection.RoleNameAlreadyExist
        role = self.role_repo.create(role)
        return role

    def find_by_id(self, role_id: int):
        validation.validate_id(role_id)
        role: Role = self.role_repo.find(role_id)
        permissions = self.role_repo.find_permission(role)
        role.list_permissions = permissions
        if role:
            return role
        raise error_collection.RecordNotFound

    def search(self, name: str) -> List[Role]:
        roles = self.role_repo.search(name)
        # https://docs.sqlalchemy.org/en/13/orm/query.html?highlight=order_by#sqlalchemy.orm.query.Query.order_by
        return roles

    def update(self, role_id: int, name: str, description: str):
        name = name.lower()
        description = description.lower()
        validation.validate_name_without_space(name)
        validation.validate_short_paragraph(description)
        role = self.role_repo.find(role_id)
        role.name = name
        role.description = description
        r: Role = self.role_repo.update(role)
        self.access_policy_repo.change_role(r, note='update role')
        return r

    def delete(self, role_id: int):
        validation.validate_id(role_id)
        role = self.role_repo.delete(role_id)
        self.access_policy_repo.change_role(role, note='delete role')
        return role

    def search_roles_with_permission(self, name: str, page: int = 1, page_size: int = 10):
        o, l = get_start_stop_pos(page, page_size)
        roles = self.role_repo.search_with_permission(name, o, l)
        return roles

    def append_role_to_user(self, user_id: int, role_id: int):
        validation.validate_id(user_id)
        validation.validate_id(role_id)
        user = self.user_repo.find(user_id)
        if not user:
            raise error_collection.RecordNotFound
        role = self.role_repo.find(role_id)
        if not role:
            raise error_collection.RecordNotFound
        u = self.user_repo.append_role(user, role)
        self.access_policy_repo.change_user(u, note='append role')
        return u

    def remove_role_from_user(self, user_id: int, role_id: int):
        validation.validate_id(user_id)
        validation.validate_id(role_id)
        user = self.user_repo.find(user_id)
        if not user:
            raise error_collection.RecordNotFound
        role = self.role_repo.find(role_id)
        if not role:
            raise error_collection.RecordNotFound
        u = self.user_repo.remove_role(user, role)
        self.access_policy_repo.change_user(u, note='remove role')
        return u

    def append_permission_to_role(self, role_id: int, permission: str):
        permission = permission.lower()
        validation.validate_id(role_id)
        validation.validate_name_without_space(permission)
        role = self.role_repo.find(role_id)
        if not role:
            raise error_collection.RecordNotFound
        self.role_repo.append_permission(role, permission)
        self.access_policy_repo.change_role(role, note='append permission')
        return role

    def find_permission_by_role_id(self, role_id: int):
        validation.validate_id(role_id)
        role = self.role_repo.find(role_id)
        if not role:
            raise error_collection.RecordNotFound
        permissions: List[PermissionPolicy] = self.role_repo.find_permission(role)
        return permissions

    def remove_permission_from_role(self, role_id: int, permission: str):
        permission = permission.lower()
        validation.validate_id(role_id)
        role = self.role_repo.find(role_id)
        if not role:
            raise error_collection.RecordNotFound
        r = self.role_repo.remove_permission(role_id, permission)
        self.access_policy_repo.change_role(r, note='remove permission')
        return r
