import json
from pprint import pprint

import pytest

from app.domain.model.process_maker.state_type import StateType
from app.infrastructure.factory_bot.user import create_or_get_normal_user
from app.infrastructure.http.fastapi_adapter.process_maker.action import action_service
from app.infrastructure.http.fastapi_adapter.process_maker.activity import activity_service
from app.infrastructure.http.fastapi_adapter.process_maker.process import process_service
from app.pkgs.api_client import client
from app.infrastructure.http.fastapi_adapter.process_maker.request import request_service
from app.pkgs.cache_tools import cache


class TestRequestAPI:

    @pytest.fixture
    def staff_1(self):
        # staff_1@test_mail.com from previous test_process_api
        staff_1 = create_or_get_normal_user("staff_1@test_mail.com")
        client.token = staff_1.token
        return staff_1

    @pytest.fixture
    def leader_1(self):
        # leader_1@test_mail.com from previous test_process_api
        return create_or_get_normal_user("leader_1@test_mail.com")

    @pytest.fixture
    def completed_process(self):
        return process_service.find_one_by_name("Test Process Workflow")

    @pytest.fixture
    @pytest.mark.run(order=41)
    def test_new_request(self, staff_1, completed_process):
        print('\ntest request api')

        # Make a POST request to the endpoint
        response = client.post("/api/request",
                               json={
                                   "process_id": completed_process.id,
                                   "title": "approve CD with test partner",
                                   "content": {"id": 0, "CD_content": "this is test content"},
                                   "note": "hey leader, please approve this request",
                                   "stakeholders": [],  # list user_id
                                   "entity_model": "",
                                   "entity_id": 0
                               })

        # Assert the response status code
        assert response.status_code == 200

        # Assert the response JSON data
        data = response.json()
        request_id = data['id']
        response = client.get(f"/api/request/{request_id}")
        # Assert the response status code
        assert response.status_code == 200

        # Assert the response JSON data
        data = response.json()
        assert "title" in data
        assert "request_data" in data
        assert "request_note" in data
        assert "current_state" in data

        # You can also assert against specific values if needed
        assert data["status"] == "active"
        assert data["request_data"][0]["value"] == '{"id": 0, "CD_content": "this is test content"}'
        assert data["request_note"][0]["note"] == 'hey leader, please approve this request'
        assert data["user_id"] == staff_1.id
        assert data["current_state"]["state_type"] == StateType.start
        yield request_service.find_one_request(data['id'])

    @pytest.mark.run(order=42)
    def test_find_one_request(self, test_new_request):
        # Make a GET request to the endpoint
        response = client.get(f"/api/request/{test_new_request.id}")
        # Assert the response status code
        assert response.status_code == 200
        # Assert the response JSON data
        data = response.json()
        assert "title" in data
        assert "request_data" in data
        assert "request_note" in data
        assert "current_state" in data

    @pytest.mark.run(order=43)
    def test_find_request_allow_action(self, test_new_request):
        # Make a GET request to the endpoint
        response = client.get(f"/api/request/{test_new_request.id}/allowed_action")
        # Assert the response status code
        assert response.status_code == 200
        # Assert the response JSON data
        data = response.json()
        actions_name = [a['name'] for a in data["data"]]
        actions_name.sort()
        assert actions_name == ['edit request', 'raise request']

    @pytest.mark.run(order=43)
    def test_find_request_allow_action_for_specific_user(self, test_new_request, staff_1, leader_1):
        # Make a GET request to the endpoint
        response = client.get(f"/api/request/{test_new_request.id}/allowed_action/{staff_1.id}")
        # Assert the response status code
        assert response.status_code == 200
        # Assert the response JSON data
        data = response.json()
        assert len(data['data']) == 2

        # Make a GET request to the endpoint
        response = client.get(f"/api/request/{test_new_request.id}/allowed_action/{leader_1.id}")
        # Assert the response status code
        assert response.status_code == 200
        # Assert the response JSON data
        data = response.json()
        assert len(data['data']) == 0

    @pytest.mark.run(order=44)
    def test_staff_commit_approve_action_failed(self, staff_1, test_new_request):
        # find the action
        approve_act = action_service.find_one_by_name('approve request')
        # Make a POST request to the endpoint
        response = client.post(f"/api/request/{test_new_request.id}/action/{approve_act.id}",
                               json={})

        data = response.json()
        # Assert the response status code
        assert response.status_code == 400
        assert data['error'].endswith('do not have right to commit this action')

    # @pytest.fixture
    @pytest.mark.run(order=45)
    def test_staff_raise_request(self, staff_1, leader_1, test_new_request):
        client.token = staff_1.token
        # find the action
        raise_act = action_service.find_one_by_name('raise request')
        # Make a POST request to the endpoint
        response = client.post(f"/api/request/{test_new_request.id}/action/{raise_act.id}",
                               json={})

        data = response.json()
        # Assert the response status code
        assert response.status_code == 200
        # return test_new_request
        # Make a GET request to the endpoint
        response = client.get(f"/api/request/{test_new_request.id}")
        # Assert the response status code
        pprint(response.json())

    # @pytest.fixture
    # @pytest.mark.run(order=46)
    # def test_leader_raise_request(self, staff_1, leader_1, test_new_request):
    #     client.token = staff_1.token
    #
    #     client.token = leader_1.token
    #     # find the action
    #     approve_act = action_service.find_one_by_name('approve request')
    #     # Make a POST request to the endpoint
    #     response = client.post(f"/api/request/{test_new_request.id}/action/{approve_act.id}",
    #                            json={})
    #
    #     data = response.json()
    #     pprint(data)
    #     # Assert the response status code
    #     assert response.status_code == 200
