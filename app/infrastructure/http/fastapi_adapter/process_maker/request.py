from typing import List

from fastapi import APIRouter, Request
from pydantic import BaseModel

from app.cmd import center_store
from app.domain.service.process_maker.request_service import RequestService
from app.domain.model.process_maker.request import Request
from app.infrastructure.http.fastapi_adapter.middle_ware import FastAPIMiddleware, Req

request_api = APIRouter()
middleware = center_store.container.get_singleton(FastAPIMiddleware)
request_service = center_store.container.get_singleton(RequestService)


class RequestDataPayload(BaseModel):
    name: str
    value: dict
    data_type: str = 'json'

class RequestNotePayload(BaseModel):
    note: str

class RequestStakeholderPayload(BaseModel):
    user_ids: List[int]


class RequestContent(BaseModel):
    process_id: int
    title: str
    content: dict
    note: str
    stakeholders: List[int]  # list user_id
    entity_model: str = ''
    entity_id: int = 0


class RequestResponse(BaseModel):
    process_id: int
    user_id: int
    title: str
    request_data: List[dict]
    request_note: List[dict]
    user: dict
    status: str
    entity_id: int
    entity_model: str
    created_at: str
    updated_at: str
    deleted_at: str = None


class ListRequestResponse(BaseModel):
    data: List[RequestResponse]
    page: int
    page_size: int


@request_api.post('/request', tags=['request'], response_model=RequestResponse)
@middleware.error_handler
@middleware.require_permissions()
async def create_new_request(request: Req, request_content: RequestContent):
    user_payload = request.user_payload
    req = request_service.create_request(
        process_id=request_content.process_id,
        user_id=user_payload.user.id,
        title=request_content.title,
        content=request_content.content,
        note=request_content.note,
        stakeholders=request_content.stakeholders,
        entity_model=request_content.entity_model,
        entity_id=request_content.entity_id,
    )
    return req.to_json()

@request_api.get('/request/{request_id}', tags=['request'], response_model=RequestResponse)
@middleware.error_handler
@middleware.require_permissions()
async def find_one_request(request: Req, request_id: int):
    user_payload = request.user_payload
    # todo: add a check if the user can view this request
    req = request_service.find_one_request(request_id)
    return req.to_json()


@request_api.get('/request/{request_id}/allowed_action', tags=['request'], response_model=ListRequestResponse)
@middleware.error_handler
@middleware.require_permissions()
async def find_one_request(request: Req, request_id: int):
    user_payload = request.user_payload
    actions = request_service.find_request_allowed_action(request_id, user_payload.user.id)
    return dict(data=[action.to_json() for action in actions ])


@request_api.get('/request/{request_id}/allowed_action/{specific_user_id}', tags=['request'], response_model=ListRequestResponse)
@middleware.error_handler
@middleware.require_permissions()
async def find_one_request(request: Req, request_id: int, specific_user_id: int):
    user_payload = request.user_payload
    actions = request_service.find_request_allowed_action_for_specific_user(request_id, user_payload.user.id, specific_user_id)
    return dict(data=[action.to_json() for action in actions])