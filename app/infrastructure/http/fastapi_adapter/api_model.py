from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional


class LoginReq(BaseModel):
    email: str
    password: Optional[str]


class PermissionPolicyAPI(BaseModel):
    role_id: int
    permission: str


class RoleAPI(BaseModel):
    id: int
    name: str
    description: str
    list_permissions: Optional[List[PermissionPolicyAPI]] = []
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime]


class UserAPI(BaseModel):
    id: int
    email: str
    is_confirmed: bool
    roles: List[RoleAPI]
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime]


class User2PermissionAPI(BaseModel):
    user_id: Optional[str] = ''
    role_id: Optional[int] = 0
    permission: Optional[str] = ''


class UpdatePasswordAPI(BaseModel):
    old_password: str
    new_password: str
    retype_password: str


class UserConfirm(BaseModel):
    is_confirmed: bool


class Token(BaseModel):
    token: str

