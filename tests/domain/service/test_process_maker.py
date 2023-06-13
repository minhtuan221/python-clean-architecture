from pprint import pprint

import pytest

from app.domain.model import Process
from app.domain.model.process_maker.state_type import StateType
from app.infrastructure.factory_bot.process_maker import create_work_flow


class TestProcessMakerService:

    @pytest.fixture()
    def test_process(self) -> Process:
        return create_work_flow('workflow test 1')

    @pytest.mark.run(order=1)
    def test_get_process_with_all_children(self, test_process):
        assert test_process.name == 'workflow test 1'
        assert test_process.status == 'inactive'

    @pytest.mark.run(order=2)
    def test_add_state_to_process(self, test_process, process_service):
        state_start = process_service.add_state_to_process(test_process.id, 'start', 'start',
                                                           StateType.start)

        state_approve = process_service.add_state_to_process(test_process.id, 'approve', 'approve',
                                                             StateType.normal)

        state_denied = process_service.add_state_to_process(test_process.id, 'denied', 'denied',
                                                            StateType.complete)

        state_done = process_service.add_state_to_process(test_process.id, 'done', 'done',
                                                          StateType.complete)
        test_process_json = test_process.to_json()
        states = test_process_json['state']

        assert states[0] == state_start.to_json()
        assert states[1] == state_approve.to_json()
        assert states[2] == state_denied.to_json()
        assert states[3] == state_done.to_json()

        route_start_to_approve = process_service.add_route_to_process(test_process.id, state_start.id,
                                                                      state_approve.id)

        route_approve_to_done = process_service.add_route_to_process(test_process.id, state_approve.id,
                                                                     state_done.id)

        route_approve_to_denied = process_service.add_route_to_process(test_process.id,
                                                                       state_approve.id,
                                                                       state_denied.id)

        route_approve_to_start = process_service.add_route_to_process(test_process.id,
                                                                      state_approve.id,
                                                                      state_start.id)
        test_process_json = test_process.to_json()
        states = test_process_json['state']

        assert states[0] == state_start.to_json()
        assert states[1] == state_approve.to_json()
        assert states[2] == state_denied.to_json()
        assert states[3] == state_done.to_json()

        assert states[0]['route'][0] == route_start_to_approve.to_json()
        assert states[1]['route'][0] == route_approve_to_done.to_json()
        assert states[1]['route'][1] == route_approve_to_denied.to_json()
        assert states[1]['route'][2] == route_approve_to_start.to_json()

        pprint(test_process.to_json())



