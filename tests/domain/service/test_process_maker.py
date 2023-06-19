from pprint import pprint

import pytest

from app.domain.model import Process
from app.domain.model.process_maker.state_type import StateType
from app.infrastructure.factory_bot.process_maker import create_work_flow
from app.infrastructure.http.fastapi_adapter.process_maker.process import process_service


class TestProcessMakerService:

    @pytest.fixture()
    def test_process(self) -> Process:
        return create_work_flow('workflow test 1')

    @pytest.mark.run(order=1)
    def test_get_process_with_all_children(self, test_process):
        assert test_process.name == 'workflow test 1'
        assert test_process.status == 'inactive'

    @pytest.mark.run(order=2)
    def test_add_state_to_process(self, test_process):
        state_start = process_service.add_state_to_process(test_process.id, 'start', 'start',
                                                           StateType.start)

        state_approve = process_service.add_state_to_process(test_process.id, 'approve', 'approve',
                                                             StateType.normal)

        state_denied = process_service.add_state_to_process(test_process.id, 'denied', 'denied',
                                                            StateType.complete)

        state_done = process_service.add_state_to_process(test_process.id, 'done', 'done',
                                                          StateType.complete)
        test_process_json = process_service.find_one(test_process.id).to_json()
        states = test_process_json['state']

        assert states[0]['name'] == state_start.name
        assert states[1]['name'] == state_approve.name
        assert states[2]['name'] == state_denied.name
        assert states[3]['name'] == state_done.name

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
        test_process_json = process_service.find_one(test_process.id).to_json()
        states = test_process_json['state']

        assert states[0]['name'] == state_start.name
        assert states[1]['name'] == state_approve.name
        assert states[2]['name'] == state_denied.name
        assert states[3]['name'] == state_done.name

        assert states[0]['route'][0]['current_state_id'] == route_start_to_approve.current_state_id
        assert states[1]['route'][0]['current_state_id']  == route_approve_to_done.current_state_id
        assert states[1]['route'][1]['current_state_id']  == route_approve_to_denied.current_state_id
        assert states[1]['route'][2]['current_state_id']  == route_approve_to_start.current_state_id

        assert states[0]['route'][0]['next_state_id'] == route_start_to_approve.next_state_id
        assert states[1]['route'][0]['next_state_id'] == route_approve_to_done.next_state_id
        assert states[1]['route'][1]['next_state_id'] == route_approve_to_denied.next_state_id
        assert states[1]['route'][2]['next_state_id'] == route_approve_to_start.next_state_id



