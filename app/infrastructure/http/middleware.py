import datetime
import time
import traceback
from functools import wraps
from logging import Logger

from flask import Flask, request, g
from flask import jsonify

from app.domain.usecase.user import UserService
from app.pkgs import errors
from app.pkgs.errors import Error, HttpStatusCode


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
        def wrapper(*args, **kwargs):
            try:
                res = func(*args, **kwargs)
            except Error as e:
                return jsonify(e.to_json()), e.code()
            except Exception as e:
                self.logger.error(e, exc_info=True)
                return jsonify(data=None, error=f'Unknown error: {str(e)}'), HttpStatusCode.Internal_Server_Error
            if res is not None:
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
                accept, note = self.user_service.is_accessible(payload['sub'], payload['role_ids'], payload['iat'])
                if not accept:
                    raise Error(f'Token rejected because of changing in user and role: {note}', HttpStatusCode.Unauthorized)
                g.user = payload['user']
                g.roles = payload['role_ids']
                g.permissions = payload['permissions']
                g.auth_token = token
            return f(*args, **kwargs)

        return decorated

    def require_permissions(self, *permissions):
        """
        Require on of the following permissions to pass over:
        :param permissions:
        :return:
        """
        self.permissions_list.update(permissions)

        def check_permission(fn):
            @wraps(fn)
            def permit(*args, **kwargs):
                for p in permissions:
                    if p in g.permissions:
                        return fn(*args, **kwargs)
                raise Error("permission denied", HttpStatusCode.Forbidden)

            return permit

        return check_permission


def set_logger(logger: Logger, app: Flask):
    app.logger.handlers = logger.handlers
    app.logger.setLevel(logger.level)
    @app.before_request
    def start_timer():
        g.start = time.time()

    @app.after_request
    def log_request(response):

        now = time.time()
        duration = '%2.4f ms' % ((now - g.start) * 1000)

        ip = request.headers.get('X-Forwarded-For', request.remote_addr)
        host = request.host.split(':', 1)[0]
        args = dict(request.args)
        timestamp = datetime.datetime.utcnow()

        log_params = [
            ('method', request.method, 'blue'),
            ('path', request.path, 'blue'),
            ('status', response.status_code, 'yellow'),
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

        app.logger.info(line)

        return response
