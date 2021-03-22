from typing import List

from fastapi import APIRouter, Request

from app.cmd.http import user_service, fastapi_middleware as middleware, user_role_service
from app.pkgs import errors as ec
from .api_model import LoginReq, UserAPI, UserConfirm, UpdatePasswordAPI, Token
from .middle_ware import ErrorResponse

record_not_found = ec.record_not_found

fastapi_user = APIRouter()


confirm_path = '/user/confirm/'
reset_password_path = '/user/reset_password/'


@fastapi_user.post("/admin", tags=["admin"], response_model=UserAPI)
@middleware.error_handler
@middleware.require_permissions('admin', 'admin.create')
async def create_new_user_by_admin(request: Request, e: LoginReq):
    user = user_service.create_new_user(e.email, e.password)
    return user.to_json()


@fastapi_user.post('/users', tags=["user"], response_model=Token)
@middleware.error_handler
async def sign_up(request: Request, u: LoginReq):
    email = u.email
    password = u.password
    token = user_service.sign_up_new_user(email, password,
                                          confirm_url=request.url_for('user_confirm_sign_up', token=''))
    return {'token': token}


@fastapi_user.get(confirm_path + '{token}', tags=["user"], response_model=ErrorResponse)
@middleware.error_handler
async def user_confirm_sign_up(request: Request, token: str):
    confirm = user_service.confirm_user_email(token)
    if confirm:
        return {'data': 'User confirmed. Please login again'}
    return {'error': 'User confirmation failed'}


@fastapi_user.post('/user/reset_password', tags=["user"], response_model=ErrorResponse)
@middleware.error_handler
async def user_reset_password(request: Request, u: LoginReq):
    email = u.email
    user_service.request_reset_user_password(email, confirm_url=request.url_for('user_confirm_reset_password', token=''))
    return {'data': f'Confirmation link was sent to the email {email}'}


@fastapi_user.post(reset_password_path + '{token}', tags=["user"], response_model=ErrorResponse)
@middleware.error_handler
async def user_confirm_reset_password(request: Request, token):
    confirm = user_service.confirm_reset_user_password(token)
    if confirm:
        return {'data': 'Password reset. Please check your email to receive new password'}
    return {'error': 'Reset password confirmation failed'}


@fastapi_user.post('/login', tags=["user"], response_model=Token)
@middleware.error_handler
async def login(request: Request, u: LoginReq):
    email = u.email
    password = u.password
    token = user_service.login(email, password)
    return {'token': token}


@fastapi_user.get('/users/profile', tags=["user"], response_model=UserAPI)
@middleware.error_handler
@middleware.require_permissions()
async def get_user_profile(request: Request):
    return {'user': request.headers['user'], 'roles': request.headers['roles'],
            'permission': request.headers['permissions']}


@fastapi_user.put('/users/{_id}/password', tags=["user"], response_model=UserAPI)
@middleware.error_handler
@middleware.require_permissions()
async def update_password(request: Request, _id: str, u: UpdatePasswordAPI):
    old_password = u.old_password
    new_password = u.new_password
    retype_password = u.retype_password
    user = user_service.update_password(int(_id), old_password, new_password, retype_password)
    return user.to_json()


@fastapi_user.get('/logout', tags=["user"], response_model=ErrorResponse)
@middleware.error_handler
@middleware.require_permissions()
async def logout(request: Request):
    token = middleware.get_bearer_token(request)
    r = user_service.logout(token)
    return {'data': r}

