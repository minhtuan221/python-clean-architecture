import pytest

from app.domain.model.process_maker.action_type import ActionType
from app.infrastructure.http.fastapi_adapter.process_maker.action import action_service
from app.infrastructure.http.fastapi_adapter.process_maker.target import target_service
from app.pkgs.api_client import client

test_order = 20


class TestActionAPI:

    @pytest.mark.run(order=test_order+1)
    def test_create_new_action(self):
        print('\ntest action API')
        # Make a POST request to the endpoint
        response = client.post("/api/action",
                               json={"name": "Test Action", "description": "Test Description",
                                     "action_type": ActionType.approve})

        # Assert the response status code
        assert response.status_code == 200

        # Assert the response JSON data
        data = response.json()
        assert "name" in data
        assert "description" in data
        assert "created_at" in data
        assert "updated_at" in data

        # You can also assert against specific values if needed
        assert data["name"] == "Test Action"

    @pytest.mark.run(order=test_order+2)
    def test_find_one_action(self):
        # find the action in previous test
        action = action_service.find_one_by_name("Test Action")

        # Make a GET request to the endpoint
        response = client.get(f"/api/action/{action.id}")

        # Assert the response status code
        assert response.status_code == 200

        # Assert the response JSON data
        data = response.json()
        assert "name" in data
        assert "description" in data
        assert "created_at" in data
        assert "updated_at" in data

        # You can also assert against specific values if needed
        assert data["name"] == "Test Action"

    @pytest.mark.run(order=test_order+3)
    def test_search_action(self):
        # let make some other action to make this test more sense, also inherit the action created from previous test
        client.post("/api/action",
                    json={"name": "Test Action 2", "description": "Test Description",
                          "action_type": ActionType.reject})
        client.post("/api/action",
                    json={"name": "Not in Search result", "description": "Test Description",
                          "action_type": ActionType.approve})
        client.post("/api/action",
                    json={"name": "Not in Search result", "description": "Test Description",
                          "action_type": ActionType.reject})

        # Make a GET request to the endpoint
        response = client.get("/api/action", params={"name": "Test Action"})

        # Assert the response status code
        assert response.status_code == 200

        # Assert the response JSON data
        data = response.json()
        assert "data" in data
        assert "page" in data
        assert "page_size" in data

        # You can also assert against specific values if needed
        assert len(data["data"]) == 2
        assert data["page"] == 1
        assert data["page_size"] == 10

    @pytest.mark.run(order=test_order+4)
    def test_update_action(self):
        # find the action in previous test
        action = action_service.find_one_by_name("Test Action 2")

        # Make a PUT request to the endpoint
        response = client.put(f"/api/action/{action.id}", json={"name": "Updated Action",
                                                               "description": "Updated Description",
                                                               "action_type": ActionType.approve})

        # Assert the response status code
        assert response.status_code == 200

        # Assert the response JSON data
        data = response.json()
        assert "name" in data
        assert "description" in data
        assert "created_at" in data
        assert "updated_at" in data

        # You can also assert against specific values if needed
        assert data["name"] == "Updated Action"

        # Make duplicate name return 400
        response = client.put(f"/api/action/{action.id}", json={"name": "Updated Action",
                                                               "description": "Updated Description",
                                                               "action_type": ActionType.approve})
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "data" in data

    @pytest.mark.run(order=test_order+5)
    def test_delete_action(self):
        # create an action to delete
        response = client.post("/api/action",
                               json={"name": "deleted action",
                                     "description": "Test Description",
                                     "action_type": ActionType.approve}).json()

        # Make a DELETE request to the endpoint
        response = client.delete(f"/api/action/{response['id']}")

        # Assert the response status code
        assert response.status_code == 200

        # Assert the response JSON data
        data = response.json()
        assert "name" in data
        assert "description" in data
        assert "created_at" in data
        assert "updated_at" in data

        # You can also assert against specific values if needed
        assert data["name"] == "deleted action"
        assert data["deleted_at"] is not None

    @pytest.mark.run(order=test_order + 6)
    def test_create_action_for_process(self):
        response = client.post("/api/action",
                               json={"name": "edit request", "description": "change request information",
                                     "action_type": ActionType.edit})
        assert response.status_code == 200
        # allow edit request
        edit_act = action_service.find_one(response.json()['id'])
        response = client.post("/api/action",
                               json={"name": "cancel request", "description": "cancel the request to change/fix it",
                                     "action_type": ActionType.edit})
        assert response.status_code == 200
        # allow cancel request
        cancel_act = action_service.find_one(response.json()['id'])
        response = client.post("/api/action",
                               json={"name": "raise request", "description": "approve request",
                                     "action_type": ActionType.approve})
        assert response.status_code == 200
        raise_act = action_service.find_one(response.json()['id'])
        response = client.post("/api/action",
                               json={"name": "approve request", "description": "approve request",
                                     "action_type": ActionType.approve})
        assert response.status_code == 200
        approve_act = action_service.find_one(response.json()['id'])
        response = client.post("/api/action",
                               json={"name": "deny request", "description": "deny request and it cannot be fixed",
                                     "action_type": ActionType.deny})
        assert response.status_code == 200
        deny_act = action_service.find_one(response.json()['id'])
        response = client.post("/api/action",
                               json={"name": "reject request", "description": "reject request and it can be fixed",
                                     "action_type": ActionType.reject})
        assert response.status_code == 200
        reject_act = action_service.find_one(response.json()['id'])

        # add target to action
        staff_group = target_service.find_one_by_name('staff group')
        leader_group = target_service.find_one_by_name('leader group')
        response = client.post(f"/api/action/{edit_act.id}/target/{staff_group.id}")
        assert response.status_code == 200
        response = client.post(f"/api/action/{cancel_act.id}/target/{staff_group.id}")
        assert response.status_code == 200
        response = client.post(f"/api/action/{approve_act.id}/target/{leader_group.id}")
        assert response.status_code == 200
        response = client.post(f"/api/action/{deny_act.id}/target/{leader_group.id}")
        assert response.status_code == 200
        response = client.post(f"/api/action/{reject_act.id}/target/{leader_group.id}")
        assert response.status_code == 200


