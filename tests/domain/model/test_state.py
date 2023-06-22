import pytest
from app.domain.model.state import State
from app.domain.model.state_type import StateType
from app.domain.utils.error_collection import ValidationError
from app.pkgs.errors import Error


class TestStateModel:

    @pytest.fixture
    def new_state(self):
        # Create an instance of the State model for testing
        return State(
            id=1,
            process_id=1,
            name='Test State',
            description='Test Description',
            state_type=StateType.normal
        )

    def test_validate(self, new_state):
        new_state.validate()
        assert new_state.name == 'Test State'
        assert new_state.description == 'Test Description'
        assert new_state.state_type == StateType.normal

    def test_format_attribute(self, new_state):
        new_state.name = "    TeSt   "
        new_state.description = "    test   "
        new_state.state_type = "START"
        new_state.validate()
        assert new_state.name == "TeSt"
        assert new_state.description == "test"
        assert new_state.state_type == "start"

    def test_validate_name_short(self, new_state):
        new_state.name = ""
        with pytest.raises(Error):
            new_state.validate()

    def test_validate_name_long(self, new_state):
        new_state.name = "n" * 129
        with pytest.raises(Error):
            new_state.validate()

    def test_validate_description_short(self, new_state):
        new_state.description = "   "
        new_state.validate()
        assert new_state.description == ""

    def test_validate_description_long(self, new_state):
        new_state.description = "n" * 501
        with pytest.raises(Error):
            new_state.validate()

    def test_validate_state_type(self, new_state):
        new_state.state_type = "nonexistent"
        with pytest.raises(ValidationError):
            new_state.validate()
