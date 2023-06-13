from typing import List
from fastapi import APIRouter, Depends, Request
from app.domain.model.process_maker.target import Target, TargetType
from app.domain.service.process_maker.target_service import TargetService
from app.infrastructure.http.fastapi_adapter.middle_ware import FastAPIMiddleware
from app.cmd import center_store

target_api = APIRouter()
middleware = center_store.container.get_singleton(FastAPIMiddleware)
target_service = center_store.container.get_singleton(TargetService)

from typing import List
from pydantic import BaseModel


class TargetReq(BaseModel):
    name: str
    description: str = ''
    target_type: str = TargetType.group
    group_id: int = 0


class TargetResponse(TargetReq):
    id: int
    created_at: str
    updated_at: str
    deleted_at: str = None


class ListTargetResponse(BaseModel):
    data: List[TargetResponse]
    page: int
    page_size: int


@target_api.post("/target", tags=["target"], response_model=TargetResponse)
@middleware.error_handler
@middleware.require_permissions()
async def create_new_target(request: Request, target: TargetReq):
    t = target_service.create(target.name, target.description, target.target_type, target.group_id)
    return t.to_json()


@target_api.get("/target/{target_id}", tags=["target"], response_model=TargetResponse)
@middleware.error_handler
@middleware.require_permissions()
async def find_one_target(request: Request, target_id: int):
    t = target_service.find_one(target_id)
    return t.to_json()


@target_api.get("/target", tags=["target"], response_model=ListTargetResponse)
@middleware.error_handler
@middleware.require_permissions()
async def search_targets(request: Request, name: str, page: int = 1, page_size: int = 10):
    targets = target_service.search(name, page, page_size)
    data = [target.to_json() for target in targets]
    return {"data": data, "page": page, "page_size": page_size}


@target_api.put("/target/{target_id}", tags=["target"], response_model=TargetResponse)
@middleware.error_handler
@middleware.require_permissions()
async def update_target(request: Request, target_id: int, target: TargetReq):
    t = target_service.update(
        target_id, target.name, target.description, target.target_type, target.group_id
    )
    return t.to_json()


@target_api.delete("/target/{target_id}", tags=["target"], response_model=TargetResponse)
@middleware.error_handler
@middleware.require_permissions()
async def delete_target(request: Request, target_id: int):
    t = target_service.delete(target_id)
    return t.to_json()
