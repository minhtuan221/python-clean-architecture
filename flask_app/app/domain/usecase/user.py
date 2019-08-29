from app.domain.model.user import User
from app.domain.model.blacklist_token import BlacklistToken
from app.infrastructure.persistence.user import UserRepository
from typing import List
import jwt
from datetime import datetime, timedelta
from app.domain.model import errors


class UserUsecase(object):
    user_repo: UserRepository

    def __init__(self, user_repo, public_key, secret_key=''):
        self.user_repo: UserRepository = user_repo
        self.secret_key = secret_key
        self.public_key = public_key

    def create_new_user(self, email: str, password: str, role: str):
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

    def login(self, email: str, password: str):
        user = self.user_repo.find_by_email(email)
        if user:
            if user.verify_password(password):
                token = self.encode_auth_token(user)
                # create and return token here
                return token.decode("utf-8")
            else:
                raise errors.password_verifing_failed
        raise errors.email_cannot_be_found

    def find_by_id(self, user_id: int):
        user: User = self.user_repo.find(user_id)
        if user:
            return user
        return None

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

    def encode_auth_token(self, user: User):
        """
        Generates the Auth Token
        :return: string
        """
        try:
            payload = {
                'exp': datetime.utcnow() + timedelta(days=0, hours=12, seconds=5),
                'iat': datetime.utcnow(),
                'sub': user.id
            }
            return jwt.encode(
                payload,
                self.secret_key,
                algorithm='RS256'
            )
        except Exception as e:
            raise e

    def validate_auth_token(self, auth_token) -> int:
        """
        Validates the auth token and check blacklist token
        :param auth_token:
        :return: integer|string as user_id or error string
        """
        try:
            payload = jwt.decode(
                auth_token, self.public_key, algorithms=['RS256'])
            is_blacklisted_token = self.user_repo.check_blacklist(auth_token)
            if is_blacklisted_token:
                raise errors.token_blacklisted
            else:
                return payload['sub']
        except jwt.ExpiredSignatureError:
            raise errors.token_expired
        except jwt.InvalidTokenError:
            raise errors.invalid_token
