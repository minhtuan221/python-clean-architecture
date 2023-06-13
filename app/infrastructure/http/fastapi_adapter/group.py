from typing import List

from fastapi import APIRouter, Request
from pydantic import BaseModel

from app.cmd import center_store
from app.domain.service.group_service import GroupService
from app.infrastructure.http.fastapi_adapter.middle_ware import FastAPIMiddleware

group_api = APIRouter()
middleware = center_store.container.get_singleton(FastAPIMiddleware)
group_service = center_store.container.get_singleton(GroupService)


class GroupReq(BaseModel):
    name: str
    description: str = ''


class GroupResponse(GroupReq):
    created_at: str
    updated_at: str
    deleted_at: str = None


class ListGroupResponse(BaseModel):
    data: List[GroupResponse]
    page: int
    page_size: int


@group_api.post('/group', tags=['group'], response_model=GroupResponse)
@middleware.error_handler
@middleware.require_permissions()
async def create_new_group(request: Request, group: GroupReq):
    p = group_service.create(group.name, group.description)
    return p.to_json()


@group_api.get('/group/{group_id}', tags=['group'], response_model=GroupResponse)
@middleware.error_handler
@middleware.require_permissions()
async def find_one_group(request: Request, group_id: int):
    p = group_service.find_one(group_id)
    return p.to_json()


@group_api.get('/group', tags=['group'], response_model=ListGroupResponse)
@middleware.error_handler
@middleware.require_permissions()
async def search_groups(request: Request, name: str, page: int = 1, page_size: int = 10):
    groups = group_service.search(name, page, page_size)
    data = [group.to_json() for group in groups]
    return {"data": data, "page": page, "page_size": page_size}


@group_api.put('/group/{group_id}', tags=['group'], response_model=GroupResponse)
@middleware.error_handler
@middleware.require_permissions()
async def update_group(request: Request, group_id: int, group: GroupReq):
    p = group_service.update(group_id, group.name, group.description)
    return p.to_json()


@group_api.delete('/group/{group_id}', tags=['group'], response_model=GroupResponse)
@middleware.error_handler
@middleware.require_permissions()
async def delete_group(request: Request, group_id: int):
    p = group_service.delete(group_id)
    return p.to_json()
