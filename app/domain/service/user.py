from datetime import datetime, timedelta
from typing import List, Set

import jwt

from app.domain.utils import validation
from app.domain.utils import generator
from app.domain.utils import error_collection
from app.config import Config
from app.domain.model.user import User
from app.domain.service.email import EmailService
from app.infrastructure.persistence.access_policy import AccessPolicyRepository
from app.infrastructure.persistence.blacklist_token import BlacklistTokenRepository
from app.infrastructure.persistence.user import UserRepository
from app.pkgs import errors
from app.pkgs.query import get_start_stop_pos
from app.pkgs.time_utils import time_to_int
from app.pkgs.type_check import type_check


class UserService(object):

    def __init__(self,
                 user_repo: UserRepository,
                 access_blacklist: AccessPolicyRepository,
                 blacklist_token_repo: BlacklistTokenRepository,
                 config: Config,
                 email_service: EmailService = None):
        self.user_repo: UserRepository = user_repo
        self.access_policy_repo = access_blacklist
        self.blacklist_token_repo = blacklist_token_repo
        self.secret_key = config.SECRET_KEY
        self.public_key = config.PUBLIC_KEY
        self.email_service = email_service

    def validate_user_email_password(self, email: str, password: str):
        validation.validate_email(email)
        validation.validate_password(password)
        current_user = self.user_repo.count_by_email(email)
        if current_user > 0:
            raise error_collection.EmailAlreadyExist()

    def create_new_user(self, email: str, password: str):
        email = email.lower()
        self.validate_user_email_password(email, password)
        user = User(email=email, password=password)
        user.hash_password(password)
        # set is_confirm to true until we complete setup email confirmation
        user.is_confirmed = True
        return self.user_repo.create(user)

    def sign_up_new_user(self, email: str, password: str, confirm_url: str):
        self.validate_user_email_password(email, password)
        user: User = User(email=email, password=password)
        user.hash_password(password)
        # set is_confirm to False
        user.is_confirmed = False
        u = self.user_repo.create(user)
        if self.email_service:
            self.email_service.send_confirm_email(user.email, confirm_url, template='user/activate.html')
        return u

    def confirm_user_email(self, token):
        email = None
        try:
            email = self.email_service.confirm_email(token)
        except Exception as e:
            errors.Error(str(e))
        if email:
            user = self.user_repo.find_by_email(email)
            if not user:
                raise error_collection.RecordNotFound
            if user.is_confirmed:
                raise errors.Error('Account already confirmed. Please login.', errors.HttpStatusCode.Bad_Request)
            else:
                user.is_confirmed = True
                user = self.user_repo.update(user)
                self.access_policy_repo.change_user(user, note=f'update user is_confirmed = {user.is_confirmed}')
                return True
        return False

    def request_reset_user_password(self, email: str, confirm_url: str):
        user = self.user_repo.find_by_email(email)
        if not user:
            raise error_collection.RecordNotFound
        if self.email_service:
            self.email_service.send_confirm_email(user.email, confirm_url, template='user/reset_password.html')
        return user

    def confirm_reset_user_password(self, token):
        email = None
        try:
            email = self.email_service.confirm_email(token)
        except Exception as e:
            errors.Error(str(e))
        if email:
            user = self.user_repo.find_by_email(email)
            if not user:
                raise error_collection.RecordNotFound
            new_password = generator.gen_reset_password()
            user.hash_password(new_password)
            user = self.user_repo.update(user)
            self.access_policy_repo.change_user(user, note=f'update user password')
            self.email_service.send_reset_password(user.email, new_password)
            return True
        return False

    def login(self, email: str, password: str):
        validation.validate_email(email)
        user, roles, permissions = self.user_repo.find_user_for_auth(email)
        if user:
            if user.verify_password(password):
                role_ids = []
                for r in roles:
                    role_ids.append(r.id)
                permissions_name: Set[str] = set()
                for p in permissions:
                    permissions_name.add(p.permission)
                other_info = {
                    'user': {
                        'id': user.id,
                        'email': user.email,
                        'is_confirmed': user.is_confirmed
                    },
                    'role_ids': role_ids,
                    'permissions': list(permissions_name)
                }
                token = self.encode_auth_token(user, other_payload_info=other_info)
                # create and return token here
                return token.decode("utf-8")
            else:
                raise error_collection.PasswordVerifyingFailed
        raise error_collection.EmailCannotBeFound

    def logout(self, auth_token: str):
        t = self.blacklist_token_repo.add_token(auth_token)
        return f'logout at: {t.blacklisted_on}'

    def find_by_id(self, user_id: int):
        validation.validate_id(user_id)
        user = self.user_repo.find(user_id)
        if user:
            return user
        raise error_collection.RecordNotFound

    def find_user_info_by_id(self, user_id: int):
        validation.validate_id(user_id)
        user, roles, permissions = self.user_repo.find_all_user_info_by_id(user_id)
        user.roles = roles
        if user:
            return user, permissions
        raise error_collection.RecordNotFound

    def search(self, email: str, page=1, page_size=10) -> List[User]:
        o, l = get_start_stop_pos(page, page_size)
        users = self.user_repo.search_with_roles(email, offset=o, limit=l)
        return users

    @type_check
    def update_password(self, user_id: int, old_password: str, new_password: str, retype_password: str):
        if new_password != retype_password:
            raise errors.Error(
                'New Password and retype password is not matched')
        validation.validate_password(new_password)
        user = self.find_by_id(user_id)
        if not user:
            raise error_collection.RecordNotFound
        if user.verify_password(old_password):
            # confirm old password
            user.hash_password(new_password)
            user = self.user_repo.update(user)
            self.access_policy_repo.change_user(user, note=f'update user password')
        return user

    @type_check
    def update_is_confirmed(self, user_id: int, is_confirmed: bool):
        user = self.find_by_id(user_id)
        if not user:
            raise error_collection.RecordNotFound
        user.is_confirmed = is_confirmed
        user = self.user_repo.update(user)
        self.access_policy_repo.change_user(user, note=f'update user is_confirmed = {user.is_confirmed}')
        return user

    def validate_access_policy(self, user_id: int, role_ids: List[int], token_iat_int: int):
        checker = self.access_policy_repo.find_for_token_validation(user_id, role_ids)
        # print(checker.to_json(), time_to_int(checker.denied_before), token_iat_int)
        if checker is None:
            return True
        if time_to_int(checker.denied_before) > token_iat_int:
            raise errors.Error(f'Token rejected because of changing in user and role: {checker.note}',
                               errors.HttpStatusCode.Unauthorized)
        return True

    def delete(self, user_id: int):
        validation.validate_id(user_id)
        user = self.user_repo.delete(user_id)
        if not user:
            raise error_collection.RecordNotFound
        self.access_policy_repo.change_user(user, note='delete user')
        return user

    def encode_auth_token(self, user: User, other_payload_info: dict):
        """
        Generates the Auth Token
        :return: string
        """
        try:
            payload = {
                'exp': datetime.utcnow() + timedelta(hours=72, seconds=5),
                'iat': datetime.utcnow(),
                'sub': user.id,
            }
            payload.update(other_payload_info)
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
            payload: dict = jwt.decode(
                auth_token, self.public_key, algorithms=['RS256'])
            is_confirmed = payload['user']['is_confirmed']
            if not is_confirmed:
                raise errors.Error('User is not confirmed', errors.HttpStatusCode.Unauthorized)
            is_blacklisted_token = self.blacklist_token_repo.is_blacklist(auth_token)
            if is_blacklisted_token:
                raise error_collection.TokenBlacklisted
            else:
                return payload
        except jwt.ExpiredSignatureError:
            raise error_collection.TokenExpired
        except jwt.InvalidTokenError:
            raise error_collection.InvalidToken
