from datetime import datetime
from typing import List, Optional

from app.domain.model import ConnectionPool
from app.domain.model import Activity
from app.domain.utils.db_helper import get_limit_offset


class ActivityRepository(object):
    def __init__(self, sql_connection: ConnectionPool):
        self.db = sql_connection

    def create(self, activity: Activity) -> Activity:
        with self.db.new_session() as db:
            activity.created_at = datetime.now()
            activity.updated_at = datetime.now()
            db.session.add(activity)
        return activity

    def find_one(self, activity_id: int) -> Optional[Activity]:
        with self.db.new_session() as db:
            activity: Activity = db.session.query(Activity).filter_by(
                id=activity_id).first()
        return activity

    def find_by_name(self, name: str) -> Optional[Activity]:
        with self.db.new_session() as db:
            activity: Activity = db.session.query(Activity).filter_by(
                name=name).first()
        return activity
    
    def get_children_by_id(self, activity_id: int) -> Optional[Activity]:
        with self.db.new_session() as db:
            activity: Activity = db.session.query(Activity).filter_by(id=activity_id). \
                first()
            activity.target
        return activity

    def search(self, name: str = '', page: int = 1, page_size: int = 20) -> List[Activity]:
        limit, offset = get_limit_offset(page, page_size)
        with self.db.new_session() as db:
            query = db.session.query(Activity) \
                .filter(Activity.deleted_at == None) \
                .order_by(Activity.updated_at.desc())

            if name:
                query = query.filter(Activity.name.like(f"%{name}%"))

            activites: List[Activity] = query.offset(offset).limit(limit).all()
        return activites

    def update(self, activity: Activity) -> Activity:
        with self.db.new_session() as db:
            activity.updated_at = datetime.now()
            db.session.add(activity)
        return activity

    def delete(self, activity_id: int) -> Optional[Activity]:
        with self.db.new_session() as db:
            activity: Activity = self.find_one(activity_id)
            if not activity:
                return activity
            activity.deleted_at = datetime.now()
            db.session.add(activity)
        return activity
