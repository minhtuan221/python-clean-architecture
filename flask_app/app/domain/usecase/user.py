from app.domain.model.user import User
from app.infrastructure.persistence.user import UserRepository
from typing import List
from app.domain.usecase import errors


class UserUsecase(object):
    user_repo: UserRepository

    def __init__(self, user_repo):
        self.user_repo: UserRepository = user_repo

    def create_new_user(self, email: str, password: str, role: str) -> User:
        current_user = self.user_repo.count_by_email(email)
        if current_user > 0:
            raise errors.email_already_exist
        user = User(email=email, password=password, role_ids=role)
        user.is_confirmed = True
        self.user_repo.create(user)
        return user
        
    def sign_up_new_user(self, email, password, role) -> User:
        user = User(email=email, password=password, role_ids=role)
        user.is_confirmed = False
        self.user_repo.create(user)
        return user

    def login(self, email: str, password: str) -> User:
        user = self.user_repo.find_by_email(email)
        if user.password == password:
            pass
        # create and return token here
        return user

    def find_by_id(self, user_id: int) -> User:
        user: User = self.user_repo.find(user_id)
        return user

    def search(self, email: str) -> List[User]:
        users = self.user_repo.search(email)
        return users

    def update(self, user_id: int, user: User):
        user = self.user_repo.update(user_id, user)
        return user

    def update_password(self, user_id: int, old_password: str, new_password: str, retype_password: str):
        user = self.user_repo.update(user_id, user)
        return user

    def update_is_confirmed(self, user_id: int, is_confirmed: bool):
        user = self.user_repo.update(user_id, user)
        return user

    def delete(self, user_id: int):
        self.user_repo.delete(user_id)
        return None
