from typing import List

from fastapi import APIRouter, Request
from pydantic import BaseModel

from app.cmd import center_store
from app.domain.service.process import ProcessService
from .middle_ware import FastAPIMiddleware

process_api = APIRouter()
middleware = center_store.container.get_singleton(FastAPIMiddleware)
process_service = center_store.container.get_singleton(ProcessService)


class ProcessReq(BaseModel):
    name: str
    description: str = ''


class ProcessResponse(ProcessReq):
    created_at: str
    updated_at: str
    deleted_at: str = None


@process_api.post('/process', tags=['process'], response_model=ProcessResponse)
@middleware.error_handler
@middleware.require_permissions()
async def create_new_process(request: Request, process: ProcessReq):
    p = process_service.create(process.name, process.description)
    return p.to_json()


@process_api.get('/process/{_id}', tags=['process'], response_model=ProcessResponse)
@middleware.error_handler
@middleware.require_permissions()
async def find_one_process(request: Request, _id: int):
    p = process_service.find_one(_id)
    return p.to_json()


@process_api.get('/process', tags=['process'], response_model=ProcessResponse)
@middleware.error_handler
@middleware.require_permissions()
async def search_process(request: Request, name: str = '', page: int = 1, page_size: int = 10):
    processes = process_service.search(name, page, page_size)
    # use dict to add more information such as total record
    return dict(data=[p.to_json() for p in processes], page=page, page_size=page_size)


@process_api.put('/process/{_id}', tags=['process'], response_model=ProcessResponse)
@middleware.error_handler
@middleware.require_permissions()
async def update_process(request: Request, _id: int, process: ProcessReq):
    p = process_service.update(_id, process.name, process.description)
    return p.to_json()


@process_api.delete('/process/{_id}', tags=['process'], response_model=ProcessResponse)
@middleware.error_handler
@middleware.require_permissions()
async def delete_process(request: Request, _id: int):
    p = process_service.delete(_id)
    return p.to_json()
