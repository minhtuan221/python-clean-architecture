from datetime import datetime
from typing import List, Optional

from app.domain.model import ConnectionPool
from app.domain.model import RequestData
from app.domain.utils.db_helper import get_limit_offset


class RequestDataRepository(object):
    def __init__(self, sql_connection: ConnectionPool):
        self.db = sql_connection

    def create(self, data: RequestData) -> RequestData:
        with self.db.new_session() as db:
            data.created_at = datetime.now()
            data.updated_at = datetime.now()
            db.session.add(data)
        return data

    def find_one(self, data_id: int) -> Optional[RequestData]:
        with self.db.new_session() as db:
            data: RequestData = db.session.query(RequestData).filter_by(
                id=data_id).filter(RequestData.deleted_at == None).first()
        return data

    def search(self, request_id: int, page: int = 1, page_size: int = 20) -> List[RequestData]:
        limit, offset = get_limit_offset(page, page_size)
        with self.db.new_session() as db:
            query = db.session.query(RequestData) \
                .filter(RequestData.deleted_at == None) \
                .filter(RequestData.request_id == request_id) \
                .order_by(RequestData.updated_at.desc())

            data_list: List[RequestData] = query.offset(offset).limit(limit).all()
        return data_list

    def update(self, data: RequestData) -> RequestData:
        with self.db.new_session() as db:
            data.updated_at = datetime.now()
            db.session.add(data)
        return data

    def delete(self, data_id: int) -> Optional[RequestData]:
        with self.db.new_session() as db:
            data: RequestData = self.find_one(data_id)
            if not data:
                return data
            data.deleted_at = datetime.now()
            db.session.add(data)
        return data
