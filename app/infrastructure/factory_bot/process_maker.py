import pytest

from app.cmd.center_store import container
from app.domain.model.process_maker.state_type import StateType
from app.domain.service.process_maker.process_service import ProcessService
from app.pkgs.cache_tools import cache


@pytest.fixture
def process_service():
    return container.get_singleton(ProcessService)


@cache()
def create_work_flow(name: str = 'approval process 1', des: str = 'testing'):
    process_service = container.get_singleton(ProcessService)
    return process_service.create(name, des)
