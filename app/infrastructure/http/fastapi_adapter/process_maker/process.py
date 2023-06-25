from typing import List

from fastapi import APIRouter, Request
from pydantic import BaseModel

from app.cmd import center_store
from app.domain.service.process_maker.process_service import ProcessService
from app.infrastructure.http.fastapi_adapter.middle_ware import FastAPIMiddleware

process_api = APIRouter()
middleware = center_store.container.get_singleton(FastAPIMiddleware)
process_service = center_store.container.get_singleton(ProcessService)


class ProcessReq(BaseModel):
    name: str
    description: str = ''


class ProcessResponse(ProcessReq):
    state: List[dict]
    created_at: str
    updated_at: str
    deleted_at: str = None


class ListProcessResponse(BaseModel):
    data: List[ProcessResponse]
    page: int
    page_size: int


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
    p = process_service.find_one(_id, with_children=True)
    return p.to_json()


@process_api.get('/process', tags=['process'], response_model=ListProcessResponse)
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


# state API

class StateReq(BaseModel):
    name: str
    description: str = ''
    state_type: str = 'start'

@process_api.post('/process/{process_id}/state', tags=['process'], response_model=ProcessResponse)
@middleware.error_handler
@middleware.require_permissions()
async def add_state_to_process(request: Request, process_id: int, body: StateReq):
    state = process_service.add_state_to_process(process_id, body.name, body.description, body.state_type)
    return state.to_json()

@process_api.get('/process/{process_id}/state/{state_id}', tags=['process'], response_model=ProcessResponse)
@middleware.error_handler
@middleware.require_permissions()
async def find_state_on_process(request: Request, process_id: int, state_id: int):
    state = process_service.find_state_on_process(process_id, state_id)
    return state.to_json()

@process_api.put('/process/{process_id}/state/{state_id}', tags=['process'], response_model=ProcessResponse)
@middleware.error_handler
@middleware.require_permissions()
async def update_state_on_process(request: Request, process_id: int, state_id: int, body: StateReq):
    state = process_service.update_state_on_process(process_id, state_id, body.name, body.description, body.state_type)
    return state.to_json()

@process_api.delete('/process/{process_id}/state/{state_id}', tags=['process'], response_model=ProcessResponse)
@middleware.error_handler
@middleware.require_permissions()
async def remove_state_from_process(request: Request, process_id: int, state_id: int):
    state = process_service.remove_state_from_process(process_id, state_id)
    return state.to_json()

@process_api.post('/process/{process_id}/state/{state_id}/activity/{activity_id}', tags=['process'], response_model=ProcessResponse)
@middleware.error_handler
@middleware.require_permissions()
async def add_activity_to_state(request: Request, process_id: int, state_id: int, activity_id: int):
    state = process_service.add_activity_to_state(process_id, state_id, activity_id)
    return state.to_json()

@process_api.delete('/process/{process_id}/state/{state_id}/activity/{activity_id}', tags=['process'], response_model=ProcessResponse)
@middleware.error_handler
@middleware.require_permissions()
async def remove_activity_from_state(request: Request, process_id: int, state_id: int, activity_id: int):
    state = process_service.remove_activity_from_state(process_id, state_id, activity_id)
    return state.to_json()


# route API
class RouteReq(BaseModel):
    current_state_id: int
    next_state_id: int = 0

@process_api.post('/process/{process_id}/route', tags=['process'], response_model=ProcessResponse)
@middleware.error_handler
@middleware.require_permissions()
async def add_route_to_process(request: Request, process_id: int, body: RouteReq):
    route = process_service.add_route_to_process(process_id, body.current_state_id, body.next_state_id)
    return route.to_json()

@process_api.get('/process/{process_id}/route/{route_id}', tags=['process'], response_model=ProcessResponse)
@middleware.error_handler
@middleware.require_permissions()
async def find_route_on_process(request: Request, process_id: int, route_id: int):
    route = process_service.find_route_on_process(process_id, route_id)
    return route.to_json()

@process_api.put('/process/{process_id}/route/{route_id}', tags=['process'], response_model=ProcessResponse)
@middleware.error_handler
@middleware.require_permissions()
async def update_route_on_process(request: Request, process_id: int, route_id: int, body: RouteReq):
    route = process_service.update_route_on_process(process_id, route_id, body.current_state_id, body.next_state_id)
    return route.to_json()

@process_api.delete('/process/{process_id}/route/{route_id}', tags=['process'], response_model=ProcessResponse)
@middleware.error_handler
@middleware.require_permissions()
async def remove_route_from_process(request: Request, process_id: int, route_id: int):
    route = process_service.remove_route_from_process(process_id, route_id)
    return route.to_json()

@process_api.post('/process/{process_id}/route/{route_id}/activity/{activity_id}', tags=['process'], response_model=ProcessResponse)
@middleware.error_handler
@middleware.require_permissions()
async def add_activity_to_route(request: Request, process_id: int, route_id: int, activity_id: int):
    route = process_service.add_activity_to_route(process_id, route_id, activity_id)
    return route.to_json()

@process_api.delete('/process/{process_id}/route/{route_id}/activity/{activity_id}', tags=['process'], response_model=ProcessResponse)
@middleware.error_handler
@middleware.require_permissions()
async def remove_activity_from_route(request: Request, process_id: int, route_id: int, activity_id: int):
    route = process_service.remove_activity_from_route(process_id, route_id, activity_id)
    return route.to_json()

@process_api.post('/process/{process_id}/route/{route_id}/action/{action_id}', tags=['process'], response_model=ProcessResponse)
@middleware.error_handler
@middleware.require_permissions()
async def add_action_to_route(request: Request, process_id: int, route_id: int, action_id: int):
    route = process_service.add_action_to_route(process_id, route_id, action_id)
    return route.to_json()

@process_api.delete('/process/{process_id}/route/{route_id}/action/{action_id}', tags=['process'], response_model=ProcessResponse)
@middleware.error_handler
@middleware.require_permissions()
async def remove_action_from_route(request: Request, process_id: int, route_id: int, action_id: int):
    route = process_service.remove_action_from_route(process_id, route_id, action_id)
    return route.to_json()
