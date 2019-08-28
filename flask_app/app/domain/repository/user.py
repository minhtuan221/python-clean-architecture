from abc import ABC, abstractmethod
from app.domain.model.user import User
from typing import List

class UserRepositoryInterface(ABC):

    @abstractmethod
    def create(self, user: User) -> User:
        raise NotImplementedError

    @abstractmethod
    def find(self, user_id: int) -> User:
        raise NotImplementedError

    @abstractmethod
    def search(self, username: str) -> List[User]:
        raise NotImplementedError

    @abstractmethod
    def update(self, user_id: int, user: User) -> User:
        raise NotImplementedError

    @abstractmethod
    def delete(self, user_id: int):
        raise NotImplementedError
