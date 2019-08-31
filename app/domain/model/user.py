import binascii
import hashlib
import os
from collections import namedtuple
from datetime import datetime
from typing import Optional, List

from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from .base import Base
from .role import Role

class User(Base):
    __tablename__ = 'users'
    id: int = Column(Integer, primary_key=True)
    email: str = Column(String(128), unique=True)
    password: str = Column(String(255))
    is_confirmed: bool = Column(Boolean, default=False)

    roles: List[Role] = relationship("Role", secondary='user_role',
                               backref="user", lazy='dynamic')

    created_at: datetime = Column(
        DateTime, index=True, default=datetime.utcnow)
    updated_at: datetime = Column(
        DateTime, index=True, default=datetime.utcnow)
    deleted_at: Optional[datetime] = Column(DateTime, index=True)

    def to_json(self) -> dict:
        roles = []
        for r in self.roles:
            roles.append(r.to_json())
        return {
            'id': self.id,
            'email': self.email,
            'is_confirmed': self.is_confirmed,
            'roles': roles,
            'created_at': self.created_at,
            'update_at': self.updated_at,
            'deleted_at': self.deleted_at
        }

    def json(self) -> dict:
        return self.to_json()

    @staticmethod
    def from_json(d: dict):
        instance = namedtuple('User', d.keys())(*d.values())
        return instance

    def hash_password(self, password):
        """Hash a password for storing."""
        salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
        pwdhash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'),
                                      salt, 100000)
        pwdhash = binascii.hexlify(pwdhash)
        self.password = (salt + pwdhash).decode('ascii')
        return self.password

    def verify_password(self, provided_password):
        """Verify a stored password against one provided by user"""
        stored_password = self.password
        salt = stored_password[:64]
        stored_password = stored_password[64:]
        password_hash = hashlib.pbkdf2_hmac('sha512',
                                            provided_password.encode('utf-8'),
                                            salt.encode('ascii'),
                                            100000)
        password_hash = binascii.hexlify(password_hash).decode('ascii')
        return password_hash == stored_password


class UserRole(Base):
    __tablename__ = 'user_role'
    user_id: int = Column(Integer, ForeignKey('users.id'), primary_key=True)
    role_id: int = Column(Integer, ForeignKey('roles.id'), primary_key=True)
