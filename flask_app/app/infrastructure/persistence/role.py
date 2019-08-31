from app.domain.model.base import ConnectionPool
from app.domain.model.user import Role, PermissionPolicy
from datetime import datetime
from typing import List


class RoleRepository(object):
    def __init__(self, sql_connection: ConnectionPool):
        self.db = sql_connection

    def create(self, role: Role) -> Role:
        with self.db.new_session() as db:
            role.created_at = datetime.now()
            role.updated_at = datetime.now()
            db.session.add(role)
        return role

    def find(self, role_id: int) -> Role:
        with self.db.new_session() as db:
            role: Role = db.session.query(Role).filter_by(
                id=role_id).filter(Role.deleted_at == None).first()
        return role

    def search(self, name: str) -> List[Role]:
        with self.db.new_session() as db:
            roles: List[Role] = db.session.query(Role).filter(
                Role.name.like(f'%{name}%')).filter(Role.deleted_at == None).all()
        return roles

    def update(self, role: Role) -> Role:
        with self.db.new_session() as db:
            role.updated_at = datetime.now()
            db.session.add(role)
        return role

    def append_permission(self, role: Role, permission: str) -> Role:
        with self.db.new_session() as db:
            p: PermissionPolicy = PermissionPolicy(role_id=role.id, permission=permission)
            db.session.add(p)
        return role

    def find_permission(self, role: Role):
        with self.db.new_session() as db:
            p: List[PermissionPolicy] = db.session.query(Role).get(role.id).permissions.all()
        return p

    def find_permission_by_roles(self, roles: List[Role]):
        with self.db.new_session() as db:
            role_ids = []
            for r in roles:
                role_ids.append(r.id)
            p: List[PermissionPolicy] = db.session.query(PermissionPolicy).filter(
                PermissionPolicy.role_id.in_(role_ids)).all()
        return p

    def remove_permission(self, role: Role, permission: PermissionPolicy) -> Role:
        with self.db.new_session() as db:
            role.permissions.remove_permission(permission)
            db.session.add(role)
        return role

    def delete(self, role_id: int):
        with self.db.new_session() as db:
            role: Role = self.find(role_id)
            role.deleted_at = datetime.now()
            db.session.add(role)
        return role
