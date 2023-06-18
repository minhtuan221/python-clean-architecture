from datetime import datetime
from typing import List, Optional

from app.domain.model import ConnectionPool
from app.domain.model import State
from app.domain.utils.db_helper import get_limit_offset


class StateRepository(object):
    def __init__(self, sql_connection: ConnectionPool):
        self.db = sql_connection

    def create(self, state: State) -> State:
        with self.db.new_session() as db:
            state.created_at = datetime.now()
            state.updated_at = datetime.now()
            db.session.add(state)
        return state

    def find_one(self, state_id: int) -> Optional[State]:
        with self.db.new_session() as db:
            state: State = db.session.query(State).filter_by(
                id=state_id).filter(State.deleted_at == None).first()
        return state

    def find_by_name_and_parent(self,  process_id: int, name: str) -> Optional[State]:
        with self.db.new_session() as db:
            state: State = db.session.query(State) \
                .filter(State.process_id == process_id) \
                .filter(State.name == name) \
                .filter(State.deleted_at == None).first()
        return state

    def find_by_parent(self, process_id: int, state_id: int) -> Optional[State]:
        with self.db.new_session() as db:
            state: State = db.session.query(State) \
                .filter(State.process_id == process_id) \
                .filter(State.id == state_id) \
                .filter(State.deleted_at == None).first()
        return state

    def search(self, name: str = '', process_id: int = 0, page: int = 1, page_size: int = 20) -> List[State]:
        limit, offset = get_limit_offset(page, page_size)
        with self.db.new_session() as db:
            query = db.session.query(State) \
                .filter(State.deleted_at == None) \
                .order_by(State.updated_at.desc())

            if name:
                query = query.filter(State.name.like(f"%{name}%"))
            if process_id:
                query = query.filter(State.process_id == process_id)

            states: List[State] = query.offset(offset).limit(limit).all()
        return states

    def update(self, state: State) -> State:
        with self.db.new_session() as db:
            state.updated_at = datetime.now()
            db.session.add(state)
        return state

    def delete(self, state_id: int) -> Optional[State]:
        with self.db.new_session() as db:
            state: State = self.find_one(state_id)
            if not state:
                return state
            state.deleted_at = datetime.now()
            db.session.add(state)
        return state
