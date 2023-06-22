import pytest
from app.domain.model.target import Target
from app.domain.model.target_type import TargetType
from app.domain.utils.error_collection import ValidationError
from app.pkgs.errors import Error


class TestTargetModel:

    @pytest.fixture
    def new_target(self):
        # Create an instance of the Target model for testing
        return Target(
            id=1,
            name='Test Target',
            description='Test Description',
            target_type=TargetType.user,
            group_id=123
        )

    def test_validate(self, new_target):
        new_target.validate()
        assert new_target.name == 'Test Target'
        assert new_target.description == 'Test Description'
        assert new_target.target_type == TargetType.user
        assert new_target.group_id == 123

    def test_format_attribute(self, new_target):
        new_target.name = "    TeSt   "
        new_target.description = "    test   "
        new_target.target_type = "Group"
        new_target.group_id = "456"
        new_target.validate()
        assert new_target.name == "TeSt"
        assert new_target.description == "test"
        assert new_target.target_type == "group"
        assert new_target.group_id == 456

    def test_validate_name_short(self, new_target):
        new_target.name = ""
        with pytest.raises(Error):
            new_target.validate()

    def test_validate_name_long(self, new_target):
        new_target.name = "n" * 129
        with pytest.raises(Error):
            new_target.validate()

    def test_validate_description_short(self, new_target):
        new_target.description = "   "
        new_target.validate()
        assert new_target.description == ""

    def test_validate_description_long(self, new_target):
        new_target.description = "n" * 501
        with pytest.raises(Error):
            new_target.validate()

    def test_validate_target_type(self, new_target):
        new_target.target_type = "nonexistent"
        with pytest.raises(ValidationError):
            new_target.validate()

    def test_validate_group_id(self, new_target):
        new_target.group_id = -1
        with pytest.raises(ValidationError):
            new_target.validate()
