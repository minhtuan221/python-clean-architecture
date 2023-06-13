from typing import List

from fastapi import APIRouter, Request
from pydantic import BaseModel

from app.cmd import center_store
from app.domain.service.process_maker.action_service import ActionService
from app.domain.model.process_maker.action import Action
from app.infrastructure.http.fastapi_adapter.middle_ware import FastAPIMiddleware

action_api = APIRouter()
middleware = center_store.container.get_singleton(FastAPIMiddleware)
action_service = center_store.container.get_singleton(ActionService)


class ActionReq(BaseModel):
    name: str
    description: str = ''
    action_type: str = ''


class ActionResponse(ActionReq):
    target: List[dict]
    created_at: str
    updated_at: str
    deleted_at: str = None


class ListActionResponse(BaseModel):
    data: List[ActionResponse]
    page: int
    page_size: int


@action_api.post('/action', tags=['action'], response_model=ActionResponse)
@middleware.error_handler
@middleware.require_permissions()
async def create_new_action(request: Request, action: ActionReq):
    p = action_service.create(action.name, action.description, action.action_type)
    return p.to_json()


@action_api.get('/action/{action_id}', tags=['action'], response_model=ActionResponse)
@middleware.error_handler
@middleware.require_permissions()
async def find_one_action(request: Request, action_id: int):
    p = action_service.find_one(action_id)
    return p.to_json()


@action_api.get('/action', tags=['action'], response_model=ListActionResponse)
@middleware.error_handler
@middleware.require_permissions()
async def search_actions(request: Request, name: str, page: int = 1, page_size: int = 10):
    actions = action_service.search(name, page, page_size)
    data = [action.to_json() for action in actions]
    return {"data": data, "page": page, "page_size": page_size}


@action_api.put('/action/{action_id}', tags=['action'], response_model=ActionResponse)
@middleware.error_handler
@middleware.require_permissions()
async def update_action(request: Request, action_id: int, action: ActionReq):
    p = action_service.update(action_id, action.name, action.description, action.action_type)
    return p.to_json()


@action_api.delete('/action/{action_id}', tags=['action'], response_model=ActionResponse)
@middleware.error_handler
@middleware.require_permissions()
async def delete_action(request: Request, action_id: int):
    p = action_service.delete(action_id)
    return p.to_json()
