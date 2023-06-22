import pytest
from app.domain.model.group import Group
from app.domain.utils.error_collection import ValidationError
from app.pkgs.errors import Error


class TestGroupModel:

    @pytest.fixture
    def new_group(self):
        # Create an instance of the Group model for testing
        return Group(
            id=1,
            name='Test Group',
            description='Test Description',
        )

    def test_validate(self, new_group):
        new_group.validate()
        assert new_group.name == 'Test Group'
        assert new_group.description == 'Test Description'

    def test_format_attribute(self, new_group):
        new_group.name = "    TeSt   "
        new_group.description = "    test   "
        new_group.validate()
        assert new_group.name == "TeSt"
        assert new_group.description == "test"

    def test_validate_name_short(self, new_group):
        new_group.name = ""
        with pytest.raises(Error):
            new_group.validate()

    def test_validate_name_long(self, new_group):
        new_group.name = "n" * 129
        with pytest.raises(Error):
            new_group.validate()

    def test_validate_description_short(self, new_group):
        new_group.description = "   "
        new_group.validate()
        assert new_group.description == ""

    def test_validate_description_long(self, new_group):
        new_group.description = "n" * 501
        with pytest.raises(Error):
            new_group.validate()
