from datetime import datetime
from typing import Optional, List

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.domain.model import Base


class PermissionPolicy(Base):
    __tablename__ = 'permission_policy'
    role_id: int = Column(Integer, ForeignKey('roles.id'), primary_key=True)
    permission: str = Column(String(128), primary_key=True)

    def to_json(self) -> dict:
        return {
            'role_id': self.role_id,
            'permission': self.permission
        }


class Role(Base):
    __tablename__ = 'roles'
    id: int = Column(Integer, primary_key=True)
    name: str = Column(String(128), unique=True)
    description: str = Column(String(500))
    permissions = relationship("PermissionPolicy", backref="role", lazy='dynamic')
    list_permissions: List[PermissionPolicy] = []

    created_at: datetime = Column(
        DateTime, index=True, default=datetime.utcnow)
    updated_at: datetime = Column(
        DateTime, index=True, default=datetime.utcnow)
    deleted_at: Optional[datetime] = Column(DateTime, index=True)

    def to_json(self) -> dict:
        permissions = []
        for p in self.list_permissions:
            permissions.append(p.to_json())
        # print('self.permissions', self.permissions)
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'permissions': permissions,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
            'deleted_at': self.deleted_at
        }
