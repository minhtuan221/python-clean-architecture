from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import joinedload

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

    def get_children_by_id(self, action_id: int) -> Optional[Action]:
        with self.db.new_session() as db:
            action: Action = db.session.query(Action).filter_by(id=action_id). \
                first()
            action.target
        return action

    def find_by_name(self, name: str) -> Optional[Action]:
        with self.db.new_session() as db:
            action: Action = db.session.query(Action).filter_by(
                name=name).first()
        return action

    def search(self, name: str = '', page: int = 1, page_size: int = 20) -> List[Action]:
        limit, offset = get_limit_offset(page, page_size)
        with self.db.new_session() as db:
            query = db.session.query(Action) \
                .filter(Action.deleted_at == None) \
                .order_by(Action.updated_at.desc())

            if name:
                query = query.filter(Action.name.like(f"%{name}%"))

            actions: List[Action] = query.offset(offset).limit(limit).all()
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
