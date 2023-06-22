import pytest
from app.domain.model.process_maker.action import Action
from app.domain.model.process_maker.action_type import ActionType
from app.domain.utils.error_collection import ValidationError
from app.pkgs.errors import Error


class TestActionModel:

    @pytest.fixture
    def new_action(self):
        # Create an instance of the Action model for testing
        return Action(
            id=1,
            name='Test Action',
            description='Test Description',
            action_type=ActionType.edit
        )

    def test_validate(self, new_action):
        new_action.validate()
        assert new_action.name == 'Test Action'
        assert new_action.description == 'Test Description'
        assert new_action.action_type == ActionType.edit

    def test_format_attribute(self, new_action):
        new_action.name = "    TeSt   "
        new_action.description = "    test   "
        new_action.action_type = "SEND"
        new_action.validate()
        assert new_action.name == "TeSt"
        assert new_action.description == "test"
        assert new_action.action_type == "send"

    def test_validate_name_short(self, new_action):
        new_action.name = ""
        with pytest.raises(Error):
            new_action.validate()

    def test_validate_name_long(self, new_action):
        new_action.name = "n" * 129
        with pytest.raises(Error):
            new_action.validate()

    def test_validate_description_short(self, new_action):
        new_action.description = "   "
        new_action.validate()
        assert new_action.description == ""

    def test_validate_description_long(self, new_action):
        new_action.description = "n" * 501
        with pytest.raises(Error):
            new_action.validate()

    def test_validate_action_type(self, new_action):
        new_action.action_type = "non exist one"
        with pytest.raises(ValidationError):
            new_action.validate()
