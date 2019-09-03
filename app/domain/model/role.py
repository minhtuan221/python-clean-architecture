from datetime import datetime
from datetime import datetime
from typing import Optional

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from app.domain.model import Base


class Role(Base):
    __tablename__ = 'roles'
    id: int = Column(Integer, primary_key=True)
    name: str = Column(String(128), unique=True)
    description: str = Column(String(500))

    # users = relationship("UserRole", back_populates="roles",
    #                      secondary='user_role')

    permissions = relationship("PermissionPolicy", lazy='dynamic')

    created_at: datetime = Column(
        DateTime, index=True, default=datetime.utcnow)
    updated_at: datetime = Column(
        DateTime, index=True, default=datetime.utcnow)
    deleted_at: Optional[datetime] = Column(DateTime, index=True)

    def to_json(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'created_at': self.created_at,
            'update_at': self.updated_at,
            'deleted_at': self.deleted_at
        }


class PermissionPolicy(Base):
    __tablename__ = 'permission_policy'
    role_id: int = Column(Integer, ForeignKey('roles.id'), primary_key=True)
    permission: str = Column(String(128), primary_key=True)

    def to_json(self) -> dict:
        return {
            'role_id': self.role_id,
            'permission': self.permission
        }
