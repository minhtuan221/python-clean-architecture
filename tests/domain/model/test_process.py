import pytest
from app.domain.model.process_maker.process import Process, ProcessStatus
from app.domain.utils.error_collection import ValidationError
from app.pkgs.errors import Error


class TestProcessModel:

    @pytest.fixture
    def new_process(self):
        # Create an instance of the Process model for testing
        return Process(
            id=1,
            name='Test Process',
            description='Test Description',
            status=ProcessStatus.active
        )

    def test_validate(self, new_process):
        new_process.validate()
        assert new_process.name == 'Test Process'
        assert new_process.description == 'Test Description'
        assert new_process.status == ProcessStatus.active

    def test_format_attribute(self, new_process):
        new_process.name = "    TeSt   "
        new_process.description = "    test   "
        new_process.status = "INACTIVE"
        new_process.validate()
        assert new_process.name == "TeSt"
        assert new_process.description == "test"
        assert new_process.status == "inactive"

    def test_validate_name_short(self, new_process):
        new_process.name = ""
        with pytest.raises(Error):
            new_process.validate()

    def test_validate_name_long(self, new_process):
        new_process.name = "n" * 129
        with pytest.raises(Error):
            new_process.validate()

    def test_validate_description_short(self, new_process):
        new_process.description = "   "
        new_process.validate()
        assert new_process.description == ""

    def test_validate_description_long(self, new_process):
        new_process.description = "n" * 501
        with pytest.raises(Error):
            new_process.validate()

    def test_validate_status(self, new_process):
        new_process.status = "nonexistent"
        with pytest.raises(ValidationError):
            new_process.validate()
