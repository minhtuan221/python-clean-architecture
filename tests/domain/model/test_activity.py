import pytest
from app.domain.model.process_maker.activity import Activity
from app.domain.model.process_maker.activity_type import ActivityType
from app.domain.utils.error_collection import ValidationError
from app.pkgs.errors import Error


class TestActivityModel:

    @pytest.fixture
    def new_activity(self):
        # Create an instance of the Activity model for testing
        return Activity(
            id=1,
            name='Test Activity',
            description='Test Description',
            activity_type=ActivityType.send_email
        )

    def test_validate(self, new_activity):
        new_activity.validate()
        assert new_activity.name == 'Test Activity'
        assert new_activity.description == 'Test Description'
        assert new_activity.activity_type == ActivityType.send_email

    def test_format_attribute(self, new_activity):
        new_activity.name = "    TeSt   "
        new_activity.description = "    test   "
        new_activity.activity_type = "SEND_EMAIL"
        new_activity.validate()
        assert new_activity.name == "TeSt"
        assert new_activity.description == "test"
        assert new_activity.activity_type == "send_email"

    def test_validate_name_short(self, new_activity):
        new_activity.name = ""
        with pytest.raises(Error):
            new_activity.validate()

    def test_validate_name_long(self, new_activity):
        new_activity.name = "n" * 129
        with pytest.raises(Error):
            new_activity.validate()

    def test_validate_description_short(self, new_activity):
        new_activity.description = "   "
        new_activity.validate()
        assert new_activity.description == ""

    def test_validate_description_long(self, new_activity):
        new_activity.description = "n" * 501
        with pytest.raises(Error):
            new_activity.validate()

    def test_validate_activity_type(self, new_activity):
        new_activity.activity_type = "non exist one"
        with pytest.raises(ValidationError):
            new_activity.validate()
