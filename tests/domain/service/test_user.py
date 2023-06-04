import datetime
from unittest.mock import MagicMock

import pytest

from app.domain.utils import error_collection
from app.cmd.center_store import container
from app.domain.model import AccessPolicy
from app.domain.service.user import UserService
from app.domain.utils.generator import generate_email
from app.pkgs import errors
from app.pkgs.time_utils import time_to_int


class TestUserService:

    @pytest.fixture
    def user_service(self):
        return container.get_singleton(UserService)

    @pytest.fixture
    def user(self, user_service):
        email = generate_email()
        password = '1Pass@word'
        user = user_service.create_new_user(email, password)
        return user

    def test_create_new_user(self, user_service):
        email = generate_email("Test")
        password = '1Pass@word'
        user = user_service.create_new_user(email, password)
        assert user.email == email.lower()
        assert user.verify_password(password)
        assert user.is_confirmed

    def test_create_new_user_with_existing_email(self, user_service, user):
        email = user.email
        password = '1Pass@word'
        with pytest.raises(error_collection.EmailAlreadyExist):
            user_service.create_new_user(email, password)

    def test_validate_user_email_password(self, user_service, user):
        email = user.email
        password = '1Pass@word'
        with pytest.raises(error_collection.EmailAlreadyExist):
            user_service.validate_user_email_password(email, password)

    def test_sign_up_new_user(self, user_service):
        email = generate_email()
        password = '1Pass@word'
        confirm_url = 'http://example.com/confirm'
        user = user_service.sign_up_new_user(email, password, confirm_url)
        assert user.email == email.lower()
        assert user.verify_password(password)
        assert not user.is_confirmed

    def test_find_by_id(self, user_service):
        user_id = 1
        user = user_service.find_by_id(user_id)
        assert user.id == user_id

        with pytest.raises(error_collection.RecordNotFound):
            user_service.find_by_id(100)

    def test_find_user_info_by_id(self, user_service, user):
        found_user, permissions = user_service.find_user_info_by_id(user.id)
        assert found_user.id == user.id

        with pytest.raises(error_collection.RecordNotFound):
            user_service.find_user_info_by_id(100)

    def test_search(self, user_service):
        email = 'very_unique_email@example.com'
        users = user_service.search(email)
        for user in users:
            assert email == user.email

    def test_update_password(self, user_service, user):
        user_id = user.id
        old_password = '1Pass@word'
        new_password = 'New_password_1@'
        retype_password = 'New_password_1@'
        new_user = user_service.update_password(user_id, old_password, new_password, retype_password)
        assert new_user.id == user_id
        assert new_user.verify_password(new_password)

        with pytest.raises(error_collection.RecordNotFound):
            user_service.update_password(10000, old_password, new_password, retype_password)

    def test_update_is_confirmed(self, user_service):
        user_id = 1
        is_confirmed = True
        user = user_service.update_is_confirmed(user_id, is_confirmed)
        assert user.id == user_id
        assert user.is_confirmed == is_confirmed

        with pytest.raises(error_collection.RecordNotFound):
            user_service.update_is_confirmed(100, is_confirmed)

    def test_validate_access_policy(self, user_service):
        now = datetime.datetime.utcnow()
        user_service.access_policy_repo.find_for_token_validation = MagicMock(
            return_value=AccessPolicy(denied_before=now))
        user_id = 1
        role_ids = [1, 2, 3]
        token_iat_int = time_to_int(now) + 1000
        assert user_service.validate_access_policy(user_id, role_ids, token_iat_int)

        with pytest.raises(errors.Error):
            user_service.validate_access_policy(100, role_ids, token_iat_int-2000)

    def test_delete(self, user_service, user):
        user_id = user.id
        delete_user = user_service.delete(user_id)
        assert delete_user.id == user_id

        with pytest.raises(error_collection.RecordNotFound):
            user_service.delete(1000)
