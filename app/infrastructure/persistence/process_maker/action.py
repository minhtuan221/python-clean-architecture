from datetime import datetime
from typing import List, Optional

from app.domain.model import ConnectionPool
from app.domain.model import Action
from app.domain.utils.db_helper import get_limit_offset


class ActionRepository(object):
    def __init__(self, sql_connection: ConnectionPool):
        self.db = sql_connection

    def create(self, action: Action) -> Action:
        with self.db.new_session() as db:
            action.created_at = datetime.now()
            action.updated_at = datetime.now()
            db.session.add(action)
        return action

    def find_one(self, action_id: int) -> Optional[Action]:
        with self.db.new_session() as db:
            action: Action = db.session.query(Action).filter_by(
                id=action_id).first()
        return action

    def find_by_name(self, name: str) -> Optional[Action]:
        with self.db.new_session() as db:
            action: Action = db.session.query(Action).filter_by(
                name=name).first()
        return action

    def search(self, page: int = 1, page_size: int = 20) -> List[Action]:
        limit, offset = get_limit_offset(page, page_size)
        with self.db.new_session() as db:
            actions: List[Action] = db.session.query(Action).offset(offset).limit(limit).all()
        return actions

    def update(self, action: Action) -> Action:
        with self.db.new_session() as db:
            action.updated_at = datetime.now()
            db.session.add(action)
        return action

    def delete(self, action_id: int) -> Optional[Action]:
        with self.db.new_session() as db:
            action: Action = self.find_one(action_id)
            if not action:
                return action
            action.deleted_at = datetime.now()
            db.session.add(action)
        return action
