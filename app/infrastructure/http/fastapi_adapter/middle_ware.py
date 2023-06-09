from typing import Any, Union
from fastapi.responses import JSONResponse
from fastapi import Request
from pydantic import BaseModel
from fastapi import status
import datetime
import time
from functools import wraps
from logging import Logger
from typing import List

from app.domain.utils import error_collection
from app.domain.service.user import UserService
from app.pkgs import errors
from app.pkgs.errors import Error, HttpStatusCode
import traceback


class ErrorResponse(BaseModel):
    error: str
    data: Union[Any, None]


def error_handler(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            res = await func(*args, **kwargs)
            if isinstance(res, BaseModel):
                return res
            return JSONResponse(content=res)
        except Error as e:
            return JSONResponse(content=e.to_json(), status_code=status.HTTP_400_BAD_REQUEST)

    return wrapper


class UserPayload:
    user: dict
    roles: list
    permissions: List[str]


class FastAPIMiddleware(object):
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
                res = await func(*args, **kwargs)
                if isinstance(res, BaseModel):
                    return res
                return JSONResponse(content=res)
            except Error as e:
                return JSONResponse(content=e.to_json(), status_code=e.code())
            except Exception as e:
                traceback.print_exc()
                # self.logger.error(e, exc_info=True)
                return JSONResponse(content=dict(data=None, error=f'Unknown error: {str(e)}'),
                                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return wrapper

    @staticmethod
    def get_bearer_token(request: Request) -> str:
        if 'Authorization' in request.headers:
            # Flask/Werkzeug do not recognize any authentication types
            # other than Basic or Digest or bearer, so here we parse the header by
            # hand
            try:
                auth_type, token = request.headers['Authorization'].split(None, 1)
            except ValueError:
                raise error_collection.AuthorizationHeaderEmpty
        else:
            raise error_collection.AuthorizationHeaderEmpty

        # if the auth type does not match, we act as if there is no auth
        # this is better than failing directly, as it allows the callback
        # to handle special cases, like supporting multiple auth types
        if auth_type.lower() != 'bearer':
            raise error_collection.AuthorizationTypeWrong
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
        if request.method.upper() != 'OPTIONS':  # pragma: no cover
            token = self.get_bearer_token(request)
            payload = self.user_service.validate_auth_token(token)
            self.user_service.validate_access_policy(payload['sub'], payload['role_ids'], payload['iat'])
            u = UserPayload
            u.user = payload.get('user', None)
            u.roles = payload.get('role_ids', None)
            u.permissions = payload.get('permissions', None)
            return u
        return None

    def require_permissions(self, *permissions):
        """
        Require on of the following permissions to pass over:
        :param permissions:
        :return:
        """
        self.permissions_list.update(permissions)

        def check_permission(fn):
            @wraps(fn)
            async def permit(request: Request, *args, **kwargs):
                u = self._verify_auth_token(request)
                if not u:
                    # any handler for OPTION method should be here
                    raise Error("permission denied", status.HTTP_403_FORBIDDEN)
                if len(permissions) > 0:
                    for p in permissions:
                        if p in u.permissions:
                            # fastapi don't need to pass request obj to it. but we should
                            return await fn(request, *args, **kwargs)
                    raise Error("permission denied", status.HTTP_403_FORBIDDEN)
                return await fn(request, *args, **kwargs)

            return permit

        return check_permission
