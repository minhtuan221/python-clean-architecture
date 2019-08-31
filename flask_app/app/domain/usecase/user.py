from datetime import datetime, timedelta
from typing import List

import jwt

from app.domain import validator
from app.domain.model import errors
from app.domain.model.user import User
from app.infrastructure.persistence.user import UserRepository
from app.pkgs.type_check import type_check


class UserUsecase(object):

    def __init__(self, user_repo: UserRepository, public_key, secret_key=''):
        self.user_repo: UserRepository = user_repo
        self.secret_key = secret_key
        self.public_key = public_key

    def validate_user_email_password(self,  email: str, password: str):
        validator.validate_email(email)
        validator.validate_password(password)
        current_user = self.user_repo.count_by_email(email)
        if current_user > 0:
            raise errors.email_already_exist

    def create_new_user(self, email: str, password: str):
        email = email.lower()
        self.validate_user_email_password(email, password)
        user = User(email=email, password=password)
        user.hash_password(password)
        # set is_confirm to true
        user.is_confirmed = True
        self.user_repo.create(user)
        return user.to_json()

    def sign_up_new_user(self, email: str, password: str):
        self.validate_user_email_password(email, password)
        user = User(email=email, password=password)
        user.hash_password(password)
        # set is_confirm to False
        user.is_confirmed = False
        self.user_repo.create(user)
        return user.to_json()

    def login(self, email: str, password: str):
        user = self.user_repo.find_by_email(email)
        if user:
            if user.verify_password(password):
                token = self.encode_auth_token(user)
                # create and return token here
                return {'token': token.decode("utf-8")}
            else:
                raise errors.password_verifying_failed
        raise errors.email_cannot_be_found

    def find_by_id(self, user_id: int):
        user: User = self.user_repo.find(user_id)
        if user:
            user_dict = user.to_json()
            # roles = self.user_repo.find_role_by_user(user)
            # for r in roles:
            #     user_dict['roles'].append(r.to_json())
            return user_dict
        raise errors.record_not_found

    def search(self, email: str) -> List[User]:
        users = self.user_repo.search(email)
        res = []
        for u in users:
            res.append(u.to_json())
        return res

    @type_check
    def update_password(self, user_id: int, old_password: str, new_password: str, retype_password: str):
        if new_password == retype_password:
            raise errors.Error(
                'New Password and retype password is not matched')
        validator.validate_password(new_password)
        user = self.find_by_id(user_id)
        if not user:
            raise errors.record_not_found
        if user.verify_password(old_password):
            # confirm old password
            user.hash_password(new_password)
            user = self.user_repo.update(user)
        return user.to_json()

    @type_check
    def update_is_confirmed(self, user_id: int, is_confirmed: bool):
        user = self.find_by_id(user_id)
        if not user:
            raise errors.record_not_found
        user.is_confirmed = is_confirmed
        user = self.user_repo.update(user_id, user)
        return user.to_json()

    def delete(self, user_id: int):
        user = self.user_repo.delete(user_id)
        return user.to_json()

    def encode_auth_token(self, user: User):
        """
        Generates the Auth Token
        :return: string
        """
        try:
            payload = {
                'exp': datetime.utcnow() + timedelta(days=3, seconds=5),
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

    def validate_auth_token(self, auth_token):
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
