from app.domain.model.base import ConnectionPool
from app.domain.model.user import User, Role
from app.domain.model.blacklist_token import BlacklistToken
from datetime import datetime
from typing import List


class UserRepository(object):
    def __init__(self, sql_connection: ConnectionPool):
        self.db = sql_connection

    def create(self, user: User) -> User:
        with self.db.new_session() as db:
            user.created_at = datetime.now()
            user.updated_at = datetime.now()
            db.session.add(user)
        return user

    def find(self, user_id: int) -> User:
        with self.db.new_session() as db:
            user: User = db.session.query(User).filter_by(
                id=user_id).filter(User.deleted_at == None).first()
        return user
    
    def find_role_by_user(self, user: User):
        with self.db.new_session() as db:
            role: List[Role] = db.session.query(User).get(user.id).roles.all()
        return role

    def find_by_email(self, email: str) -> User:
        with self.db.new_session() as db:
            user: User = db.session.query(User).filter_by(
                email=email).filter(User.deleted_at == None).first()
        return user

    def count_by_email(self, email: str) -> int:
        with self.db.new_session() as db:
            total: int = db.session.query(User).filter_by(
                email=email).filter(User.deleted_at == None).count()
        return total

    def search(self, email: str) -> List[User]:
        with self.db.new_session() as db:
            users: List[User] = db.session.query(User).filter(
                User.email.like(f'%{email}%')).filter(User.deleted_at == None).all()
        return users

    def update(self, user: User) -> User:
        with self.db.new_session() as db:
            user.updated_at = datetime.now()
            db.session.add(user)
        return user

    def delete(self, user_id: int):
        with self.db.new_session() as db:
            user: User = self.find(user_id)
            user.deleted_at = datetime.now()
            db.session.add(user)
        return user
    
    def append_role(self, user: User, role: Role) -> User:
        with self.db.new_session() as db:
            user.roles.append(role)
            db.session.add(user)
        return user
    
    def remove_role(self, user: User, role: Role) -> User:
        with self.db.new_session() as db:
            user.roles.remove(role)
            db.session.add(user)
        return user

    def check_blacklist(self, auth_token):
        # check whether auth token has been blacklisted
        with self.db.new_session() as db:
            res = db.session.query(BlacklistToken).filter_by(
                token=str(auth_token)).first()
            if res:
                return True
            else:
                return False
