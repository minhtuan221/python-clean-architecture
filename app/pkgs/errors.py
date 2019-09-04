from functools import wraps
from logging import Logger


class HttpStatusCode(object):
    OK = 200
    Not_Modified = 304
    Bad_Request = 400
    Unauthorized = 401
    Forbidden = 403
    Not_Found = 404
    Method_Not_Allowed = 405
    Internal_Server_Error = 500
    Not_Implemented = 501


class Error(Exception):
    """Base class for exceptions in this module."""

    def __init__(self, message, error_code=HttpStatusCode.OK, data=None):
        self.message: str = message
        self.error_code: int = error_code
        self.data = data

    def to_json(self) -> dict:
        return {
            'error': self.message,
            'data': self.data
        }

    def code(self):
        return self.error_code

    def __str__(self):
        return self.message


def error_handler(func):
    """Contain handler for json and error exception. Accept only one value (not tuple) and should be a dict/list

    Arguments:
        func {[type]} -- [description]

    Returns:
        [type] -- [description]
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            res = func(*args, **kwargs)
        except Error as e:
            return e
        except Exception as e:
            return Error(f'Unknown error: {str(e)}')
        return res
    return wrapper


record_not_found = Error('Record not found')
email_already_exist = Error('Email already exist', HttpStatusCode.Bad_Request)
email_cannot_be_found = Error(
    'Email cannot be found', HttpStatusCode.Bad_Request)
password_verifying_failed = Error(
    'Password is not match', HttpStatusCode.Bad_Request)
token_expired = Error(
    'Signature expired. Please log in again', HttpStatusCode.Unauthorized)
invalid_token = Error('Invalid token. Please log in again.',
                      HttpStatusCode.Unauthorized)
token_blacklisted = Error(
    'Token blacklisted. Please log in again.', HttpStatusCode.Unauthorized)
authorization_header_empty = Error(
    'The Authorization header is either empty or has no token', HttpStatusCode.Unauthorized)
authorization_type_wrong = Error(
    'The Authorization header is wrong type or invalid', HttpStatusCode.Unauthorized)
unconfirmed_email = Error(
    'The email address is not confirmed', HttpStatusCode.Unauthorized)
reset_access_policy = Error(
    'Token expired because of changing in user and role', HttpStatusCode.Unauthorized)
role_name_already_exist = Error('role name already exist', HttpStatusCode.Bad_Request)
