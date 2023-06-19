import binascii
import hashlib
import os
from collections import namedtuple
from dataclasses import dataclass
from datetime import datetime
from typing import Optional, List

from sqlalchemy import Column, String, Integer, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from . import Base
from ._serializable import Serializable
from .role import Role


class User(Base, Serializable):
    __tablename__ = 'users'
    id: int = Column(Integer, primary_key=True)
    email: str = Column(String(128), unique=True)
    password: str = Column(String(255))
    is_confirmed: bool = Column(Boolean, default=False)

    roles: List[Role] = relationship("Role", secondary='user_role', backref="user", lazy='dynamic')
    request = relationship("Request", back_populates="user")
    group = relationship("Group", secondary='group_member', back_populates="member")
    token: str = ''

    _json_black_list: List[str] = ['password']

    def to_json(self) -> dict:
        json_data = super().to_json()  # Call the to_json method of the base class
        roles = [r.to_json() for r in self.roles]
        json_data['roles'] = roles
        return json_data

    def json(self) -> dict:
        return self.to_json()

    @staticmethod
    def from_json(d: dict):
        instance = namedtuple('User', d.keys())(*d.values())
        return instance

    def hash_password(self, password):
        """Hash a password for storing."""
        salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
        password_hash = hashlib.pbkdf2_hmac('sha512', password.encode('utf-8'),
                                            salt, 100000)
        password_hash = binascii.hexlify(password_hash)
        self.password = (salt + password_hash).decode('ascii')
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

    def __repr__(self):
        return f"User(id={self.id}, email={self.email})"


class UserRole(Base):
    __tablename__ = 'user_role'
    user_id: int = Column(Integer, ForeignKey('users.id'), primary_key=True)
    role_id: int = Column(Integer, ForeignKey('roles.id'), primary_key=True)


@dataclass
class UserInfo:
    id: int = 0
    email: str = ''
    is_confirmed: bool = False


@dataclass
class UserPayload:
    user: UserInfo = None
    roles: List[int] = None
    permissions: List[str] = None


def pack_user_payload(user: User, role_ids: List[int],
                      permissions_name: List[str]) -> dict:
    return {
        'user': {
            'id': user.id,
            'email': user.email,
            'is_confirmed': user.is_confirmed
        },
        'role_ids': role_ids,
        'permissions': list(permissions_name)
    }


def unpack_user_payload(payload: dict) -> UserPayload:
    u = UserPayload()
    if 'user' in payload:
        u.user = UserInfo(**payload['user'])
    else:
        u.user = UserInfo()
    u.roles = payload.get('role_ids', [])
    u.permissions = payload.get('permissions', [])
    return u
