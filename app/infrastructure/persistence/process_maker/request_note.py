from datetime import datetime
from typing import List, Optional

from app.domain.model import ConnectionPool
from app.domain.model import RequestNote
from app.domain.utils.db_helper import get_limit_offset


class RequestNoteRepository(object):
    def __init__(self, sql_connection: ConnectionPool):
        self.db = sql_connection

    def create(self, note: RequestNote) -> RequestNote:
        with self.db.new_session() as db:
            note.created_at = datetime.now()
            note.updated_at = datetime.now()
            db.session.add(note)
        return note

    def find_one(self, note_id: int) -> Optional[RequestNote]:
        with self.db.new_session() as db:
            note: RequestNote = db.session.query(RequestNote).filter_by(
                id=note_id).filter(RequestNote.deleted_at == None).first()
        return note

    def search(self, request_id: int, page: int = 1, page_size: int = 20) -> List[RequestNote]:
        limit, offset = get_limit_offset(page, page_size)
        with self.db.new_session() as db:
            query = db.session.query(RequestNote) \
                .filter(RequestNote.deleted_at == None) \
                .filter(RequestNote.request_id == request_id) \
                .order_by(RequestNote.updated_at.desc())

            notes: List[RequestNote] = query.offset(offset).limit(limit).all()
        return notes

    def update(self, note: RequestNote) -> RequestNote:
        with self.db.new_session() as db:
            note.updated_at = datetime.now()
            db.session.add(note)
        return note

    def delete(self, note_id: int) -> Optional[RequestNote]:
        with self.db.new_session() as db:
            note: RequestNote = self.find_one(note_id)
            if not note:
                return note
            note.deleted_at = datetime.now()
            db.session.add(note)
        return note
