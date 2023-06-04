import datetime
import time
from functools import wraps
from logging import Logger

from sanic import Sanic
from sanic.request import Request
from sanic.response import json, HTTPResponse as Response

from app.domain.service.user import UserService
from app.pkgs import errors
from app.pkgs.errors import Error, HttpStatusCode
import traceback


class Middleware(object):
    def __init__(self, a: UserService, logger: Logger):
        self.user_service = a
        self.permissions_list = set()
        self.logger = logger

    def error_handler(self, func):
        """Contain handler for json and error exception. Accept only one value (not tuple) and should be a dict/list

        Arguments:
            func {[type]} -- [description]

        Returns:
            [type] -- [description]
        """

        @wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                res = func(*args, **kwargs)
            except Error as e:
                return json(e.to_json(), status=e.code())
            except Exception as e:
                traceback.print_exc()
                self.logger.error(e, exc_info=True)
                return json(dict(data=None, error=f'Unknown error: {str(e)}'),
                            status=HttpStatusCode.Internal_Server_Error)
            if res is not None:
                return json(dict(data=res))
            return json(dict(data=[]))

        return wrapper

    @staticmethod
    def get_bearer_token(request):
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
        if auth_type.lower() != 'bearer':
            raise errors.authorization_type_wrong
        return token

    def verify_auth_token(self, f):
        @wraps(f)
        async def decorated(request: Request, *args, **kwargs):
            self._verify_auth_token(request)
            return f(request, *args, **kwargs)

        return decorated

    def _verify_auth_token(self, request: Request):
        # Flask normally handles OPTIONS requests on its own, but in the
        # case it is configured to forward those to the application, we
        # need to ignore authentication headers and let the request through
        # to avoid unwanted interactions with CORS.
        if request.method != 'OPTIONS':  # pragma: no cover
            token = self.get_bearer_token(request)
            payload = self.user_service.validate_auth_token(token)
            # print(payload)
            self.user_service.validate_access_policy(payload['sub'], payload['role_ids'], payload['iat'])
            request.headers['user'] = payload['user']
            request.headers['roles'] = payload['role_ids']
            request.headers['permissions'] = payload['permissions']
            request.headers['auth_token'] = token
        return request

    def require_permissions(self, *permissions):
        """
        Require on of the following permissions to pass over:
        :param permissions:
        :return:
        """
        self.permissions_list.update(permissions)

        def check_permission(fn):
            @wraps(fn)
            def permit(request: Request, *args, **kwargs):
                self._verify_auth_token(request)
                if len(permissions) > 0:
                    for p in permissions:
                        if p in request.headers['permissions']:
                            return fn(request, *args, **kwargs)
                    raise Error("permission denied", HttpStatusCode.Forbidden)
                return fn(request, *args, **kwargs)

            return permit

        return check_permission


def set_logger(logger: Logger, app: Sanic):
    # app.logger.handlers = logger.handlers
    # app.logger.setLevel(logger.level)
    @app.middleware('request')
    def start_timer(request):
        request.headers['start'] = time.time()

    @app.middleware('response')
    def log_request(request: Request, response: Response):
        # print(request.headers)
        if 'start' in request.headers: # CORS preflight message do not touch before request middle ware
            start = request.headers['start']

            now = time.time()
            duration = '%2.4f ms' % ((now - start) * 1000)

            ip = request.headers.get('X-Forwarded-For', request.ip)
            host = request.host.split(':', 1)[0]
            args = dict(request.args)
            timestamp = datetime.datetime.utcnow()

            log_params = [
                ('method', request.method, 'blue'),
                ('path', request.path, 'blue'),
                ('status', response.status, 'yellow'),
                ('duration', duration, 'green'),
                ('utc_time', timestamp, 'magenta'),
                ('ip', ip, 'red'),
                ('host', host, 'red'),
                ('params', args, 'blue')
            ]

            request_id = request.headers.get('X-Request-ID')
            if request_id:
                log_params.append(('request_id', request_id, 'yellow'))

            parts = []
            for name, value, _color in log_params:
                part = f'"{name}":"{value}"'
                parts.append(part)
            line = '{' + ",".join(parts) + '}'

            logger.info(line)

        return response
