from datetime import datetime
from typing import List, Optional

from app.domain.model import ConnectionPool
from app.domain.model import RequestStakeholder
from app.domain.utils.db_helper import get_limit_offset


class RequestStakeholderRepository(object):
    def __init__(self, sql_connection: ConnectionPool):
        self.db = sql_connection

    def create(self, stakeholder: RequestStakeholder) -> RequestStakeholder:
        with self.db.new_session() as db:
            stakeholder.created_at = datetime.now()
            stakeholder.updated_at = datetime.now()
            db.session.add(stakeholder)
        return stakeholder

    def find_one(self, stakeholder_id: int) -> Optional[RequestStakeholder]:
        with self.db.new_session() as db:
            stakeholder: RequestStakeholder = db.session.query(RequestStakeholder).filter_by(
                id=stakeholder_id).filter(RequestStakeholder.deleted_at == None).first()
        return stakeholder

    def search(self, request_id: int, page: int = 1, page_size: int = 20) -> List[RequestStakeholder]:
        limit, offset = get_limit_offset(page, page_size)
        with self.db.new_session() as db:
            query = db.session.query(RequestStakeholder) \
                .filter(RequestStakeholder.deleted_at == None) \
                .filter(RequestStakeholder.request_id == request_id) \
                .order_by(RequestStakeholder.updated_at.desc())

            stakeholders: List[RequestStakeholder] = query.offset(offset).limit(limit).all()
        return stakeholders

    def update(self, stakeholder: RequestStakeholder) -> RequestStakeholder:
        with self.db.new_session() as db:
            stakeholder.updated_at = datetime.now()
            db.session.add(stakeholder)
        return stakeholder

    def delete(self, stakeholder_id: int) -> Optional[RequestStakeholder]:
        with self.db.new_session() as db:
            stakeholder: RequestStakeholder = self.find_one(stakeholder_id)
            if not stakeholder:
                return stakeholder
            stakeholder.deleted_at = datetime.now()
            db.session.add(stakeholder)
        return stakeholder
