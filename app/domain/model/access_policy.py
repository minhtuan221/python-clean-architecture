import datetime

from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from typing import Optional

from .base import Base


class AccessPolicy(Base):
    """
    Checking every change/update in User, Role, PermissionPolicy model.
    Change in user's password, is_confirmed, roles -> add checker of user_id, role_id = None
    change in role's permission -> add checker of role_id, user_id = None
    """
    __tablename__ = 'access_policy'

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    user_id: int = Column(Integer, ForeignKey('users.id'), index=True)
    role_id: int = Column(Integer, ForeignKey('roles.id'), index=True)
    note: str = Column(String(250))
    denied_before: datetime.datetime = Column(DateTime, index=True, nullable=False)

    def to_json(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'role_id': self.role_id,
            'note': self.note,
            'denied_before': self.denied_before
        }

    def __repr__(self):
        return f'<UserUpdateChecker: user_id: {self.user_id}, role_id: {self.role_id}'
