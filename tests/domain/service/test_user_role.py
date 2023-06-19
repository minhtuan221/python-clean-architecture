import pytest

from app.cmd.center_store import container
from app.domain.service.user import UserService
from app.domain.service.user_role import UserRoleService
from app.domain.utils.generator import generate_email


class TestUserRoleService:

    @pytest.fixture
    def user_role_service(self):
        return container.get_singleton(UserRoleService)

    @pytest.fixture
    def user_service(self):
        return container.get_singleton(UserService)

    @pytest.fixture
    def new_user(self, user_service):
        email = generate_email()
        return user_service.create_new_user(email, '1Pass@word')

    def test_create_and_find_role(self, user_role_service):
        role_name = 'test_create_and_find_role'
        role_description = 'this is role for testing'
        role = user_role_service.create_new_role(role_name, role_description)
        role = user_role_service.find_by_id(role.id)
        assert role.name == role_name
        assert role.description == role_description

    def test_search_role(self, user_role_service):
        user_role_service.create_new_role('foo', 'this is role for testing')
        user_role_service.create_new_role('bar', 'this is role for testing')
        user_role_service.create_new_role('bla', 'this is role for testing')
        user_role_service.create_new_role('bla_bla', 'this is role for testing')
        roles = user_role_service.search('foo')
        assert roles[0].name == 'foo'
        assert len(roles) == 1
        roles = user_role_service.search('bla')
        assert roles[0].name == 'bla'
        assert roles[1].name == 'bla_bla'
        assert len(roles) == 2

    def test_update_role(self, user_role_service):
        role_name = 'test_update_role'
        role_description = 'this is role for testing'
        role = user_role_service.create_new_role(role_name, role_description)
        updated_name = 'updated_test'
        updated_description = 'updated description'
        updated_role = user_role_service.update(role.id, updated_name, updated_description)
        assert updated_role.name == updated_name
        assert updated_role.description == updated_description

    def test_delete_role(self, user_role_service):
        role_name = 'test_delete_role'
        role_description = 'this is role for testing'
        role = user_role_service.create_new_role(role_name, role_description)
        deleted_role = user_role_service.delete(role.id)
        assert deleted_role.id == role.id

    def test_append_role_to_user(self, user_role_service, user_service, new_user):
        role_name = 'test_append_role_to_user'
        role_description = 'this is role for testing'
        role = user_role_service.create_new_role(role_name, role_description)
        user = new_user
        user_with_role = user_role_service.append_role_to_user(user.id, role.id)
        # assert role in user_with_role.roles

    def test_remove_role_from_user(self, user_role_service, new_user):
        role_name = 'test_remove_role_from_user'
        role_description = 'this is role for testing'
        role = user_role_service.create_new_role(role_name, role_description)
        user = new_user
        user_with_role = user_role_service.append_role_to_user(user.id, role.id)
        # assert role in user_with_role.roles.all()
        user_without_role = user_role_service.remove_role_from_user(user.id, role.id)
        # assert role not in user_without_role.roles

    def test_append_permission_to_role(self, user_role_service):
        role_name = 'test_append_permission_to_role'
        role_description = 'this is role for testing'
        role = user_role_service.create_new_role(role_name, role_description)
        role_with_permission = user_role_service.append_permission_to_role(role.id, 'read')
        permissions = user_role_service.find_permission_by_role_id(role.id)
        assert len(permissions) == 1
        assert permissions[0].permission == 'read'

    def test_remove_permission_from_role(self, user_role_service):
        role_name = 'test_remove_permission_from_role'
        role_description = 'this is role for testing'
        role = user_role_service.create_new_role(role_name, role_description)
        role_with_permission = user_role_service.append_permission_to_role(role.id, 'read')
        role_without_permission = user_role_service.remove_permission_from_role(role.id, 'read')
        permissions = user_role_service.find_permission_by_role_id(role.id)
        assert len(permissions) == 0
