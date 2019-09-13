from datetime import datetime
from typing import List

from app.domain.model import ConnectionPool
from app.domain.model.role import Role, PermissionPolicy


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

    def find_by_name(self, name: str) -> Role:
        with self.db.new_session() as db:
            role: Role = db.session.query(Role).filter_by(
                name=name).filter(Role.deleted_at == None).first()
        return role

    def search(self, name: str) -> List[Role]:
        with self.db.new_session() as db:
            roles: List[Role] = db.session.query(Role).filter(
                Role.name.like(f'%{name}%')).filter(Role.deleted_at == None).all()
        return roles

    def search_with_permission(self, name: str, offset: int = 0, limit: int = 10) -> List[Role]:
        with self.db.new_session() as db:
            roles: List[Role] = db.session.query(Role).filter(
                Role.name.like(f'%{name}%')).filter(Role.deleted_at == None).order_by(Role.updated_at.desc()).offset(offset).limit(limit).all()
            # for r in roles:
            #     r.list_permissions = r.permissions.all()
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

    def find_one_permission(self, role_id: int, permission: str) -> PermissionPolicy:
        with self.db.new_session() as db:
            p: PermissionPolicy = db.session.query(PermissionPolicy).filter(PermissionPolicy.role_id == role_id).filter(
                PermissionPolicy.permission == permission).first()
        return p

    def find_permission_by_role_ids(self, role_ids: List[int]):
        with self.db.new_session() as db:
            p: List[PermissionPolicy] = db.session.query(PermissionPolicy).filter(
                PermissionPolicy.role_id.in_(role_ids)).all()
        return p

    def remove_permission(self, role_id: int, permission: str) -> Role:
        with self.db.new_session() as db:
            db.session.query(PermissionPolicy).filter(PermissionPolicy.role_id == role_id).filter(
                PermissionPolicy.permission == permission).delete()
        return Role(id=role_id)

    def delete(self, role_id: int):
        with self.db.new_session() as db:
            role: Role = self.find(role_id)
            role.deleted_at = datetime.now()
            db.session.add(role)
        return role
