import pytest

from app.domain.model.process_maker.action_type import ActionType
from app.infrastructure.http.fastapi_adapter.process_maker.action import action_service
from app.pkgs.api_client import client


class TestActionAPI:

    @pytest.mark.run(order=11)
    def test_create_new_action(self):
        print('test action API')
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

    @pytest.mark.run(order=12)
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

    @pytest.mark.run(order=13)
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

    @pytest.mark.run(order=14)
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

    @pytest.mark.run(order=15)
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
