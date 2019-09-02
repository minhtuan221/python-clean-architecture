from flask import jsonify, g, request
from functools import wraps
from app.pkgs.errors import Error, HttpStatusCode
from app.pkgs import errors
from app.domain.usecase.user import UserService
import traceback


class Middleware(object):
    def __init__(self, a: UserService):
        self.user_service = a
        self.permissions_list = set()

    @staticmethod
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
                return jsonify(e.to_json()), e.code()
            except Exception as e:
                traceback.print_exc()
                return jsonify(data=None, error=f'Unknown error: {str(e)}'), HttpStatusCode.Internal_Server_Error
            if res is not None:
                if type(res) is Error:
                    return jsonify(res.to_json()), res.code()
                return jsonify(data=res)
            return jsonify(data=[])

        return wrapper

    @staticmethod
    def get_bearer_token():
        if 'Authorization' in request.headers:
            # Flask/Werkzeug do not recognize any authentication types
            # other than Basic or Digest or bearer, so here we parse the header by
            # hand
            try:
                auth_type, token = request.headers['Authorization'].split(None, 1)
            except ValueError:
                raise errors.authorization_header_empty
        else:
            raise errors.authorization_header_empty

        # if the auth type does not match, we act as if there is no auth
        # this is better than failing directly, as it allows the callback
        # to handle special cases, like supporting multiple auth types
        if auth_type != 'Bearer':
            raise errors.authorization_type_wrong
        return token

    def verify_auth_token(self, f):
        @wraps(f)
        def decorated(*args, **kwargs):

            # Flask normally handles OPTIONS requests on its own, but in the
            # case it is configured to forward those to the application, we
            # need to ignore authentication headers and let the request through
            # to avoid unwanted interactions with CORS.
            if request.method != 'OPTIONS':  # pragma: no cover
                token = self.get_bearer_token()
                payload = self.user_service.validate_auth_token(token)
                # print(payload)
                accept = self.user_service.is_accessible(payload['sub'], payload['role_ids'], payload['iat'])
                if not accept:
                    raise errors.reset_access_policy
                g.user = payload['user']
                g.roles = payload['role_ids']
                g.permissions = payload['permissions']
                g.auth_token = token
            return f(*args, **kwargs)

        return decorated

    def require_permissions(self, *permissions):
        self.permissions_list.update(permissions)

        def check_permission(fn):
            @wraps(fn)
            def permit(*args, **kwargs):
                p_set = set(permissions)
                g_permissions = set(g.permissions)
                if p_set.issubset(g_permissions):
                    return fn(*args, **kwargs)
                raise Error("permission denied")
            return permit

        return check_permission
