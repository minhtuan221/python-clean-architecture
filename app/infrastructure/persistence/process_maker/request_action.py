from datetime import datetime
from typing import List, Optional

from app.domain.model import ConnectionPool
from app.domain.model import RequestAction
from app.domain.utils.db_helper import get_limit_offset


class RequestActionRepository(object):
    def __init__(self, sql_connection: ConnectionPool):
        self.db = sql_connection

    def create(self, action: RequestAction) -> RequestAction:
        with self.db.new_session() as db:
            action.created_at = datetime.now()
            action.updated_at = datetime.now()
            db.session.add(action)
        return action

    def find_one(self, action_id: int) -> Optional[RequestAction]:
        with self.db.new_session() as db:
            action: RequestAction = db.session.query(RequestAction).filter_by(
                id=action_id).filter(RequestAction.deleted_at == None).first()
        return action

    def search(self, request_id: int, page: int = 1, page_size: int = 20) -> List[RequestAction]:
        limit, offset = get_limit_offset(page, page_size)
        with self.db.new_session() as db:
            query = db.session.query(RequestAction) \
                .filter(RequestAction.deleted_at == None) \
                .filter(RequestAction.request_id == request_id) \
                .order_by(RequestAction.updated_at.desc())

            actions: List[RequestAction] = query.offset(offset).limit(limit).all()
        return actions

    def update(self, action: RequestAction) -> RequestAction:
        with self.db.new_session() as db:
            action.updated_at = datetime.now()
            db.session.add(action)
        return action

    def delete(self, action_id: int) -> Optional[RequestAction]:
        with self.db.new_session() as db:
            action: RequestAction = self.find_one(action_id)
            if not action:
                return action
            action.deleted_at = datetime.now()
            db.session.add(action)
        return action
