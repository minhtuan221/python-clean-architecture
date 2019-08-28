class Error(Exception):
    """Base class for exceptions in this module."""

    def __init__(self, expression, error_code):
        self.expression = expression
        self.error_code = error_code


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


def requires_permission(sPermission):
    def decorator(fn):
        def decorated(*args, **kwargs):
            lPermissions = get_permissions(current_user_id())
            if sPermission in lPermissions:
                return fn(*args, **kwargs)
            raise Exception("permission denied")
        return decorated
    return decorator


email_already_exist = Error('Email already exist', HttpStatusCode.Bad_Request)
