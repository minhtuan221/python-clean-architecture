import pytest

from app.cmd.center_store import container
from app.domain.model.process_maker.state_type import StateType
from app.domain.service.process_maker.process import ProcessService


@pytest.fixture
def process_service():
    return container.get_singleton(ProcessService)


@pytest.fixture
def process_1(process_service):
    process_1 = process_service.create('approval process 1', 'testing')

    state_start = process_service.add_state_to_process(process_1.id, 'start', 'start',
                                                       StateType.start)

    state_approve = process_service.add_state_to_process(process_1.id, 'approve', 'approve',
                                                         StateType.normal)

    state_denied = process_service.add_state_to_process(process_1.id, 'denied', 'denied',
                                                        StateType.complete)

    state_done = process_service.add_state_to_process(process_1.id, 'done', 'done',
                                                      StateType.complete)

    route_start_to_approve = process_service.add_route_to_process(process_1.id, state_start.id,
                                                                  state_approve.id)

    route_approve_to_done = process_service.add_route_to_process(process_1.id, state_approve.id,
                                                                 state_done.id)

    route_approve_to_denied = process_service.add_route_to_process(process_1.id, state_approve.id,
                                                                   state_denied.id)

    route_approve_to_start = process_service.add_route_to_process(process_1.id, state_approve.id,
                                                                  state_start.id)
    return process_1
