from datetime import datetime
from typing import Optional, List

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.domain.model import Base
from app.domain.model._serializable import Serializable


class PermissionPolicy(Base):
    __tablename__ = 'permission_policy'
    role_id: int = Column(Integer, ForeignKey('roles.id'), primary_key=True)
    permission: str = Column(String(128), primary_key=True)

    def to_json(self) -> dict:
        return {
            'role_id': self.role_id,
            'permission': self.permission
        }


class Role(Base, Serializable):
    __tablename__ = 'roles'
    id: int = Column(Integer, primary_key=True)
    name: str = Column(String(128), unique=True)
    description: str = Column(String(500))
    permissions = relationship("PermissionPolicy", backref="role", lazy='dynamic')
    list_permissions: List[PermissionPolicy] = []

    def to_json(self) -> dict:
        json_data = super().to_json()  # Call the to_json method of the base class
        json_data['permissions'] = [p.to_json() for p in self.list_permissions]
        return json_data
