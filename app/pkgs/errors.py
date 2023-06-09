from functools import wraps


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
    message: str = ''
    error_code: int = 0
    data: dict = None

    def __init__(self, message: str = 'there is no error here', error_code=HttpStatusCode.OK, data=None):
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


