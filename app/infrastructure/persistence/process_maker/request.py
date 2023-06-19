from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import joinedload

from app.domain.model import ConnectionPool
from app.domain.model import Request, RequestNote, RequestData, RequestStakeholder, RequestAction
from app.domain.utils.db_helper import get_limit_offset


class RequestRepository(object):
    def __init__(self, sql_connection: ConnectionPool):
        self.db = sql_connection

    def create(self, request: Request) -> Request:
        with self.db.new_session() as db:
            request.created_at = datetime.now()
            request.updated_at = datetime.now()
            db.session.add(request)
        return request

    def find_one(self, request_id: int) -> Optional[Request]:
        with self.db.new_session() as db:
            request: Request = db.session.query(Request).filter_by(
                id=request_id).first()
            if request:
                for act in request.request_action:
                    act.action
                request.request_note
                request.request_stakeholder
                request.request_data
                request.current_state
        return request

    def find_one_by_title(self, title: str) -> Optional[Request]:
        with self.db.new_session() as db:
            request: Request = db.session.query(Request).filter(Request.title == title).first()
        return request

    def search(self, title: str = '', page: int = 1, page_size: int = 20) -> List[Request]:
        limit, offset = get_limit_offset(page, page_size)
        with self.db.new_session() as db:
            query = db.session.query(Request) \
                .filter(Request.deleted_at == None) \
                .order_by(Request.updated_at.desc())

            if title:
                query = query.filter(Request.title.like(f"%{title}%"))

            requests: List[Request] = query.offset(offset).limit(limit).all()
        return requests

    def update(self, request: Request) -> Request:
        with self.db.new_session() as db:
            request.updated_at = datetime.now()
            db.session.add(request)
        return request

    def delete(self, request_id: int) -> Optional[Request]:
        with self.db.new_session() as db:
            request: Request = self.find_one(request_id)
            if not request:
                return request
            request.deleted_at = datetime.now()
            db.session.add(request)
        return request

    def get_children_by_request_id(self, request_id: int) -> Optional[Request]:
        with self.db.new_session() as db:
            request: Request = db.session.query(Request)\
                .filter_by(id=request_id)\
                .options(joinedload(Request.request_note),
                        joinedload(Request.request_data),
                        joinedload(Request.request_stakeholder),
                        joinedload(Request.request_action))\
                .first()
        return request
