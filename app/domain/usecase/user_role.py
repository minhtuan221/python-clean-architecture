from typing import List

from app.domain import validator
from app.domain.model import errors
from app.domain.model.user import Role, User, PermissionPolicy
from app.infrastructure.persistence.role import RoleRepository
from app.infrastructure.persistence.user import UserRepository


class UserRoleService(object):

    def __init__(self, role_repo: RoleRepository, user_repo: UserRepository):
        self.role_repo = role_repo
        self.user_repo = user_repo

    def create_new_role(self, name: str, description: str):
        name = name.lower()
        description = description.lower()
        validator.validate_name(name)
        role = Role(name=name, description=description)
        role = self.role_repo.create(role)
        return role.to_json()

    def find_by_id(self, role_id: int):
        role: Role = self.role_repo.find(role_id)
        if role:
            return role
        raise errors.record_not_found

    def search(self, name: str) -> List[Role]:
        roles = self.role_repo.search(name)
        # https://docs.sqlalchemy.org/en/13/orm/query.html?highlight=order_by#sqlalchemy.orm.query.Query.order_by
        return roles

    def update(self, role_id: int, name: str, description: str):
        name = name.lower()
        description = description.lower()
        validator.validate_name(name)
        role = self.find_by_id(role_id)
        role.name = name
        role.description = description
        r: Role = self.role_repo.update(role)
        return r

    def delete(self, role_id: int):
        role = self.role_repo.delete(role_id)
        return role

    def append_role_to_user(self, user_id: int, role_id: int):
        user = self.user_repo.find(user_id)
        if not user:
            raise errors.record_not_found
        role = self.role_repo.find(role_id)
        if not role:
            raise errors.record_not_found
        u = self.user_repo.append_role(user, role)
        return u.to_json()

    def remove_role_to_user(self, user_id: int, role_id: int):
        user = self.user_repo.find(user_id)
        if not user:
            raise errors.record_not_found
        role = self.role_repo.find(role_id)
        if not role:
            raise errors.record_not_found
        u = self.user_repo.remove_role(user, role)
        return u.to_json()

    def append_permission_to_role(self, role_id: int, permission: str):
        role = self.role_repo.find(role_id)
        if not role:
            raise errors.record_not_found
        self.role_repo.append_permission(role, permission)
        return role.to_json()

    def view_permission_to_role(self, role_id: int):
        role = self.role_repo.find(role_id)
        if not role:
            raise errors.record_not_found
        permissions: List[PermissionPolicy] = self.role_repo.find_permission(role)
        permissions_list = []
        for p in permissions:
            permissions_list.append(p.to_json())
        return permissions_list

    def view_permission_to_user(self, user_id: int):
        user: User = self.user_repo.find(user_id)
        if not user:
            raise errors.record_not_found
        role = self.user_repo.find_role_by_user(user)
        if not role:
            raise errors.record_not_found
        permissions = self.role_repo.find_permission_by_roles(role)
        permissions_list = []
        for p in permissions:
            permissions_list.append(p.to_json()['permission'])
        return permissions_list

    def remove_permission_to_role(self, role_id: int, permission: str):
        role = self.role_repo.find(role_id)
        if not role:
            raise errors.record_not_found
        permission = PermissionPolicy(role_id=role_id, permission=permission)
        self.role_repo.remove_permission(role, permission)
        return role.to_json()
