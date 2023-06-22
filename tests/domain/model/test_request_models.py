import pytest
from app.domain.model.process_maker.request import Request, RequestNote, RequestData, RequestStakeholder, RequestAction
from app.domain.utils.error_collection import ValidationError
from app.pkgs.errors import Error


class TestRequestModel:

    @pytest.fixture
    def new_request(self):
        # Create an instance of the Request model for testing
        return Request(
            id=1,
            title='Test Request',
            user_id=1,
            process_id=1,
            current_state_id=1,
            status='active',
            entity_model='',
            entity_id=0,
        )

    def test_validate(self, new_request):
        new_request.validate()
        assert new_request.title == 'Test Request'
        assert new_request.status == 'active'

    def test_validate_invalid_title(self, new_request):
        # Test case where title is too long
        new_request.title = 'A' * 501
        with pytest.raises(Error):
            new_request.validate()

    def test_validate_invalid_status(self, new_request):
        # Test case where status is invalid
        new_request.status = 'invalid_status'
        with pytest.raises(ValidationError):
            new_request.validate()


class TestRequestNoteModel:

    @pytest.fixture
    def new_request_note(self):
        # Create an instance of the RequestNote model for testing
        return RequestNote(
            id=1,
            user_id=1,
            request_id=1,
            note_type='user_note',
            status='active',
            note='This is a test note',
        )

    def test_validate(self, new_request_note):
        new_request_note.validate()
        assert new_request_note.note_type == 'user_note'
        assert new_request_note.status == 'active'

    def test_validate_invalid_note_type(self, new_request_note):
        # Test case where note_type is invalid
        new_request_note.note_type = 'invalid_note_type'
        with pytest.raises(ValidationError):
            new_request_note.validate()

    def test_validate_invalid_status(self, new_request_note):
        # Test case where status is invalid
        new_request_note.status = 'invalid_status'
        with pytest.raises(ValidationError):
            new_request_note.validate()


class TestRequestDataModel:

    @pytest.fixture
    def new_request_data(self):
        # Create an instance of the RequestData model for testing
        return RequestData(
            id=1,
            request_id=1,
            data_type='json',
            status='active',
            name='content',
            value='{"key": "value"}',
        )

    def test_validate(self, new_request_data):
        new_request_data.validate()
        assert new_request_data.data_type == 'json'
        assert new_request_data.status == 'active'

    def test_validate_invalid_data_type(self, new_request_data):
        # Test case where data_type is invalid
        new_request_data.data_type = 'invalid_data_type'
        with pytest.raises(ValidationError):
            new_request_data.validate()

    def test_validate_invalid_status(self, new_request_data):
        # Test case where status is invalid
        new_request_data.status = 'invalid_status'
        with pytest.raises(ValidationError):
            new_request_data.validate()


class TestRequestStakeholderModel:

    @pytest.fixture
    def new_request_stakeholder(self):
        # Create an instance of the RequestStakeholder model for testing
        return RequestStakeholder(
            id=1,
            request_id=1,
            stakeholder_id=1,
            stakeholder_type='user',
        )

    def test_validate(self, new_request_stakeholder):
        new_request_stakeholder.validate()
        assert new_request_stakeholder.stakeholder_type == 'user'

    def test_validate_invalid_stakeholder_type(self, new_request_stakeholder):
        # Test case where stakeholder_type is invalid
        new_request_stakeholder.stakeholder_type = 'invalid_stakeholder_type'
        with pytest.raises(ValidationError):
            new_request_stakeholder.validate()


class TestRequestActionModel:

    @pytest.fixture
    def new_request_action(self):
        # Create an instance of the RequestAction model for testing
        return RequestAction(
            id=1,
            request_id=1,
            action_id=1,
            user_id=1,
            route_id=1,
            status='active',
        )

    def test_validate(self, new_request_action):
        new_request_action.validate()
        assert new_request_action.status == 'active'

    def test_validate_invalid_status(self, new_request_action):
        # Test case where status is invalid
        new_request_action.status = 'invalid_status'
        with pytest.raises(ValidationError):
            new_request_action.validate()


