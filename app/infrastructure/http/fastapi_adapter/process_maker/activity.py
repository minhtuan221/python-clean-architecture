from typing import List

from fastapi import APIRouter, Request
from pydantic import BaseModel

from app.cmd import center_store
from app.domain.model.process_maker.activity import Activity
from app.domain.service.process_maker.activity_service import ActivityService
from app.infrastructure.http.fastapi_adapter.middle_ware import FastAPIMiddleware

activity_api = APIRouter()
middleware = center_store.container.get_singleton(FastAPIMiddleware)
activity_service = center_store.container.get_singleton(ActivityService)


class ActivityReq(BaseModel):
    name: str
    description: str = ''
    activity_type: str = ''


class ActivityResponse(ActivityReq):
    created_at: str
    updated_at: str
    deleted_at: str = None


class ListActivityResponse(BaseModel):
    data: List[ActivityResponse]
    page: int
    page_size: int


@activity_api.post('/activity', tags=['activity'], response_model=ActivityResponse)
@middleware.error_handler
@middleware.require_permissions()
async def create_new_activity(request: Request, activity: ActivityReq):
    a = activity_service.create(activity.name, activity.description, activity.activity_type)
    return a.to_json()


@activity_api.get('/activity/{activity_id}', tags=['activity'], response_model=ActivityResponse)
@middleware.error_handler
@middleware.require_permissions()
async def find_one_activity(request: Request, activity_id: int):
    a = activity_service.find_one(activity_id)
    return a.to_json()


@activity_api.get('/activity', tags=['activity'], response_model=ListActivityResponse)
@middleware.error_handler
@middleware.require_permissions()
async def search_activities(request: Request, name: str, page: int = 1, page_size: int = 10):
    activities = activity_service.search(name, page, page_size)
    data = [activity.to_json() for activity in activities]
    return {"data": data, "page": page, "page_size": page_size}


@activity_api.put('/activity/{activity_id}', tags=['activity'], response_model=ActivityResponse)
@middleware.error_handler
@middleware.require_permissions()
async def update_activity(request: Request, activity_id: int, activity: ActivityReq):
    a = activity_service.update(activity_id, activity.name, activity.description, activity.activity_type)
    return a.to_json()


@activity_api.delete('/activity/{activity_id}', tags=['activity'], response_model=ActivityResponse)
@middleware.error_handler
@middleware.require_permissions()
async def delete_activity(request: Request, activity_id: int):
    a = activity_service.delete(activity_id)
    return a.to_json()
