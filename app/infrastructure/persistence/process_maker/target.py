from datetime import datetime
from typing import List, Optional

from app.domain.model import ConnectionPool
from app.domain.model import Target
from app.domain.utils.db_helper import get_limit_offset


class TargetRepository(object):
    def __init__(self, sql_connection: ConnectionPool):
        self.db = sql_connection

    def create(self, target: Target) -> Target:
        with self.db.new_session() as db:
            target.created_at = datetime.now()
            target.updated_at = datetime.now()
            db.session.add(target)
        return target

    def find_one(self, target_id: int) -> Optional[Target]:
        with self.db.new_session() as db:
            target: Target = db.session.query(Target).filter_by(
                id=target_id).first()
        return target

    def find_by_name(self, name: str) -> Optional[Target]:
        with self.db.new_session() as db:
            target: Target = db.session.query(Target).filter_by(
                name=name).first()
        return target

    def search(self, name: str = '', page: int = 1, page_size: int = 20) -> List[Target]:
        limit, offset = get_limit_offset(page, page_size)
        with self.db.new_session() as db:
            query = db.session.query(Target) \
                .filter(Target.deleted_at == None) \
                .order_by(Target.updated_at.desc())

            if name:
                query = query.filter(Target.name.like(f"%{name}%"))

            targets: List[Target] = query.offset(offset).limit(limit).all()
        return targets

    def update(self, target: Target) -> Target:
        with self.db.new_session() as db:
            target.updated_at = datetime.now()
            db.session.add(target)
        return target

    def delete(self, target_id: int) -> Optional[Target]:
        with self.db.new_session() as db:
            target: Target = self.find_one(target_id)
            if not target:
                return target
            target.deleted_at = datetime.now()
            db.session.add(target)
        return target
