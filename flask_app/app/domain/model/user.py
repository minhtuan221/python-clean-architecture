from datetime import datetime, timedelta
from typing import Optional
from collections import namedtuple
from sqlalchemy import Column, String, Integer, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base
import jwt
import hashlib
import binascii
import os


class User(Base):
    __tablename__ = 'users'
    id: int = Column(Integer, primary_key=True)
    email: str = Column(String(128), unique=True)
    password: str = Column(String(255))
    role_ids: str = Column(Text)
    is_confirmed: bool = Column(Boolean, default=False)

    roles = relationship("UserRole", back_populates="user")

    created_at: datetime = Column(
        DateTime, index=True, default=datetime.utcnow)
    updated_at: datetime = Column(
        DateTime, index=True, default=datetime.utcnow)
    deleted_at: Optional[datetime] = Column(DateTime, index=True)

    def to_json(self) -> dict:
        return {
            'id': self.id,
            'email': self.email,
            'created_at': self.created_at,
            'update_at': self.updated_at,
            'deleted_at': self.deleted_at
        }

    def json(self) -> dict:
        return self.to_json()

    def from_json(self, d: dict):
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
        pwdhash = hashlib.pbkdf2_hmac('sha512',
                                      provided_password.encode('utf-8'),
                                      salt.encode('ascii'),
                                      100000)
        pwdhash = binascii.hexlify(pwdhash).decode('ascii')
        return pwdhash == stored_password


class UserRole(Base):
    __tablename__ = 'user_role'
    user_id: int = Column(Integer, ForeignKey('users.id'), primary_key=True)
    role_id: int = Column(Integer, ForeignKey('roles.id'), primary_key=True)
    role = relationship("Role", back_populates="users")
    user = relationship("User", back_populates="roles")


class Role(Base):
    __tablename__ = 'roles'
    id: int = Column(Integer, primary_key=True)
    name: str = Column(String(128), unique=True)
    description: str = Column(String(500), unique=True)
    users = relationship("UserRole", back_populates="role")


class PermissionPolicy(Base):
    __tablename__ = 'permission_policy'
    role_id: int = Column(Integer, ForeignKey('roles.id'), primary_key=True)
    permission: str = Column(String(128), primary_key=True)
