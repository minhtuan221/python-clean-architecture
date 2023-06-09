import traceback
from dataclasses import dataclass

from app.pkgs.errors import Error, HttpStatusCode


# old code:
# email_already_exist = Error("Email already exists")
# new code after refactoring
@dataclass
class EmailAlreadyExist(Error):
    message: str = "Email already exists"
    error_code: int = HttpStatusCode.Bad_Request


@dataclass
class RecordNotFound(Error):
    message: str = 'Record not found'
    error_code: int = HttpStatusCode.Bad_Request


@dataclass
class EmailCannotBeFound(Error):
    message: str = 'Email cannot be found'
    error_code: int = HttpStatusCode.Bad_Request


@dataclass
class PasswordVerifyingFailed(Error):
    message: str = 'Password is not matched'
    error_code: int = HttpStatusCode.Bad_Request


@dataclass
class TokenExpired(Error):
    message: str = 'Signature expired. Please log in again'
    error_code: int = HttpStatusCode.Unauthorized


@dataclass
class InvalidToken(Error):
    message: str = 'Invalid token. Please log in again.'
    error_code: int = HttpStatusCode.Unauthorized


@dataclass
class TokenBlacklisted(Error):
    message: str = 'Token blacklisted. Please log in again.'
    error_code: int = HttpStatusCode.Unauthorized


@dataclass
class AuthorizationHeaderEmpty(Error):
    message: str = 'The Authorization header is either empty or has no token'
    error_code: int = HttpStatusCode.Unauthorized


@dataclass
class AuthorizationTypeWrong(Error):
    message: str = 'The Authorization header is wrong type or invalid'
    error_code: int = HttpStatusCode.Unauthorized


@dataclass
class UnconfirmedEmail(Error):
    message: str = 'The email address is not confirmed'
    error_code: int = HttpStatusCode.Unauthorized


@dataclass
class ResetAccessPolicy(Error):
    message: str = 'Token expired because of changing in user and role'
    error_code: int = HttpStatusCode.Unauthorized


@dataclass
class RoleNameAlreadyExist(Error):
    message: str = 'Role name already exists'
    error_code: int = HttpStatusCode.Bad_Request


@dataclass
class RecordAlreadyExist(Error):
    message: str = 'Record already exists'
    error_code: int = HttpStatusCode.Bad_Request


def test_raise_error():
    try:
        raise EmailAlreadyExist("adfakljdjkal")
    except Exception:
        traceback.print_exc()
    try:
        raise EmailAlreadyExist("12123")
    except Exception:
        traceback.print_exc()
    try:
        raise EmailAlreadyExist("nothing")
    except Exception:
        traceback.print_exc()
