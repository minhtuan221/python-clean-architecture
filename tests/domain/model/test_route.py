import pytest
from app.domain.model.process_maker.route import Route
from app.domain.utils.error_collection import ValidationError
from app.pkgs.errors import Error


class TestRouteModel:

    @pytest.fixture
    def new_route(self):
        # Create an instance of the Route model for testing
        return Route(
            id=1,
            process_id=1,
            current_state_id=1,
            next_state_id=2,
        )

    def test_validate(self, new_route):
        new_route.validate()
        assert new_route.process_id == 1
        assert new_route.current_state_id == 1

    def test_validate_process_id(self, new_route):
        new_route.process_id = -1
        with pytest.raises(Error):
            new_route.validate()

    def test_validate_current_state_id(self, new_route):
        new_route.current_state_id = 0
        with pytest.raises(Error):
            new_route.validate()
