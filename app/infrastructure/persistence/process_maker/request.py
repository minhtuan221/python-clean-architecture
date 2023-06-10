from datetime import datetime
from typing import List, Optional

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
        return request

    def search(self, title: str = '', page: int = 1, page_size: int = 20) -> List[Request]:
        limit, offset = get_limit_offset(page, page_size)
        with self.db.new_session() as db:
            query = db.session.query(Request)
            if title:
                query = query.filter(Request.title.ilike(f'%{title}%'))
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
            request: Request = db.session.query(Request).filter_by(
                id=request_id). \
                options(db.joinedload(Request.request_note).
                        order_by(RequestNote.updated_at.desc()),
                        db.joinedload(Request.request_data).
                        order_by(RequestData.updated_at.desc()),
                        db.joinedload(Request.request_stakeholder),
                        db.joinedload(Request.request_action).
                        order_by(RequestAction.updated_at.desc())). \
                first()
        return request
