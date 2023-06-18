from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import joinedload

from app.domain.model import ConnectionPool, GroupMember
from app.domain.model import Group
from app.domain.utils.db_helper import get_limit_offset


class GroupRepository(object):
    def __init__(self, sql_connection: ConnectionPool):
        self.db = sql_connection

    def create(self, group: Group) -> Group:
        with self.db.new_session() as db:
            group.created_at = datetime.now()
            group.updated_at = datetime.now()
            db.session.add(group)
        return group

    def find_one(self, group_id: int) -> Optional[Group]:
        with self.db.new_session() as db:
            group: Group = db.session.query(Group).filter_by(id=group_id).first()
        return group

    def find_by_name(self, name: str) -> Optional[Group]:
        with self.db.new_session() as db:
            group: Group = db.session.query(Group).filter_by(name=name).first()
        return group

    def search(self, name: str = '', page: int = 1, page_size: int = 20) -> List[Group]:
        limit, offset = get_limit_offset(page, page_size)
        with self.db.new_session() as db:
            query = db.session.query(Group).filter(Group.deleted_at == None).order_by(Group.updated_at.desc())

            if name:
                query = query.filter(Group.name.like(f"%{name}%"))

            groups: List[Group] = query.offset(offset).limit(limit).all()
        return groups

    def is_user_in_group(self, group_id: int, user_id: int) -> Optional[GroupMember]:
        with self.db.new_session() as db:
            group_member = db.session.query(GroupMember)\
                .filter(GroupMember.group_id == group_id)\
                .filter(GroupMember.user_id == user_id).first()
        return group_member

    def update(self, group: Group) -> Group:
        with self.db.new_session() as db:
            group.updated_at = datetime.now()
            db.session.add(group)
        return group

    def delete(self, group_id: int) -> Optional[Group]:
        with self.db.new_session() as db:
            group: Group = self.find_one(group_id)
            if not group:
                return group
            group.deleted_at = datetime.now()
            db.session.add(group)
        return group
