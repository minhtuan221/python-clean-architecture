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

        assert len(completed_process.state) == 4
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
        assert "title" in data
        assert "request_data" in data
        assert "request_note" in data
        assert "current_state" in data
        assert "user" in data

        # You can also assert against specific values if needed
        assert data["status"] == "active"
        assert data["request_data"][0]["value"] == '{"id": 0, "CD_content": "this is test content"}'
        assert data["request_note"][0]["note"] == 'hey leader, please approve this request'
        assert data["user"]["id"] == staff_1.id
        assert data["current_state"]["state_type"] == StateType.start
        return request_service.find_one_request(data['id'])

    @pytest.mark.run(order=42)
    def test_find_one_request(self, test_new_request):
        # Make a GET request to the endpoint
        response = client.get(f"/api/request/{test_new_request.id}")
        # Assert the response status code
        pprint(response.json())
        assert response.status_code == 200
        # Assert the response JSON data
        data = response.json()
        assert "title" in data
        assert "request_data" in data
        assert "request_note" in data
        assert "current_state" in data
        assert "user" in data

    @pytest.mark.run(order=43)
    def test_find_request_allow_action(self, test_new_request):
        # Make a GET request to the endpoint
        response = client.get(f"/api/request/{test_new_request.id}/allowed_action")
        # Assert the response status code
        assert response.status_code == 200
        # Assert the response JSON data
        data = response.json()
        pprint(data)
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



