from app.domain.model.base import ConnectionPool
from app.domain.model.user import User
from app.domain.repository.user import UserRepositoryInterface
from datetime import datetime
from typing import List


class UserRepository(UserRepositoryInterface):
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
            user: User = db.session.query(User).filter_by(id=user_id).filter(User.deleted_at==None).first()
        return user

    def find_by_email(self, email: str) -> User:
        with self.db.new_session() as db:
            user: User = db.session.query(User).filter_by(email=email).first()
        return user
    
    def count_by_email(self, email: str) -> int:
        with self.db.new_session() as db:
            total: int = db.session.query(User).filter_by(email=email).scalar()
        return total

    def search(self, email: str) -> List[User]:
        with self.db.new_session() as db:
            users: List[User] = db.session.query(User).filter(
                User.email.like(f'%{email}%')).filter(User.deleted_at==None).all()
        return users

    def update(self, user_id: int, user: User) -> User:
        with self.db.new_session() as db:
            current_user: User = db.session.query(User) \
                .filter_by(id=user_id) \
                .first()
            current_user.role_ids = user.role_ids
            current_user.password = user.password
            current_user.updated_at = datetime.now()
        return current_user

    def delete(self, user_id: int):
        with self.db.new_session() as db:
            user: User = db.session.query(User).filter(
                User.id == user_id).first()
            user.deleted_at = datetime.now()
