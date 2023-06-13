from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import joinedload

from app.domain.model import ConnectionPool
from app.domain.model import Process
from app.domain.utils.db_helper import get_limit_offset


class ProcessRepository(object):
    def __init__(self, sql_connection: ConnectionPool):
        self.db = sql_connection

    def create(self, process: Process) -> Process:
        with self.db.new_session() as db:
            process.created_at = datetime.now()
            process.updated_at = datetime.now()
            db.session.add(process)
        return process

    def find_one(self, process_id: int) -> Optional[Process]:
        with self.db.new_session() as db:
            process: Process = db.session.query(Process).filter_by(
                id=process_id).filter(Process.deleted_at == None).first()
        return process

    def get_children_by_process_id(self, process_id: int) -> Optional[Process]:
        with self.db.new_session() as db:
            process: Process = db.session.query(Process).filter_by(id=process_id). \
                first()
            for s in process.state:
                s.route
        return process

    def find_by_name(self, name: str) -> Optional[Process]:
        with self.db.new_session() as db:
            process: Process = db.session.query(Process).filter_by(name=name).filter(Process.deleted_at == None).first()
        return process

    def search(self, name: str = '', page: int = 1, page_size: int = 20) -> List[Process]:
        limit, offset = get_limit_offset(page, page_size)
        with self.db.new_session() as db:
            query = db.session.query(Process) \
                .filter(Process.deleted_at == None) \
                .order_by(Process.updated_at.desc())

            if name:
                query = query.filter(Process.name.like(f"%{name}%"))

            processes: List[Process] = query.offset(offset).limit(limit).all()
        return processes

    def update(self, process: Process) -> Process:
        with self.db.new_session() as db:
            process.updated_at = datetime.now()
            db.session.add(process)
        return process

    def delete(self, process_id: int) -> Optional[Process]:
        with self.db.new_session() as db:
            process: Process = self.find_one(process_id)
            if not process:
                return process
            process.deleted_at = datetime.now()
            db.session.add(process)
        return process
