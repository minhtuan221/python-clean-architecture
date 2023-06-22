import pprint

import pytest

from app.domain.model.process_maker.target import TargetType
from app.infrastructure.http.fastapi_adapter.group import group_service
from app.infrastructure.http.fastapi_adapter.process_maker.target import target_service
from app.pkgs.api_client import client


class TestTargetAPI:

    @pytest.mark.run(order=11)
    def test_create_new_target(self):
        # Make a POST request to the endpoint
        response = client.post("/api/target",
                               json={"name": "Test Target", "description": "Test Description",
                                     "target_type": TargetType.group, "group_id": 1})

        # Assert the response status code
        assert response.status_code == 200

        # Assert the response JSON data
        data = response.json()
        assert "name" in data
        assert "description" in data
        assert "created_at" in data
        assert "updated_at" in data

        # You can also assert against specific values if needed
        assert data["name"] == "Test Target"

    @pytest.mark.run(order=12)
    def test_find_one_target(self):
        # find the target in previous test
        target = target_service.find_one_by_name("Test Target")

        # Make a GET request to the endpoint
        response = client.get(f"/api/target/{target.id}")

        # Assert the response status code
        assert response.status_code == 200

        # Assert the response JSON data
        data = response.json()
        assert "name" in data
        assert "description" in data
        assert "created_at" in data
        assert "updated_at" in data

        # You can also assert against specific values if needed
        assert data["name"] == "Test Target"

    @pytest.mark.run(order=13)
    def test_search_target(self):
        # let make some other target to make this test more sense, also inherit the target created from previous test
        response = client.post("/api/target",
                    json={"name": "Test Target 2", "description": "Test Description",
                          "target_type": TargetType.user, "group_id": 0})
        if response.status_code != 200:
            raise ValueError(str(response.json()))
        assert response.status_code == 200
        response = client.post("/api/target",
                    json={"name": "Not in Search result 1", "description": "Test Description",
                          "target_type": TargetType.group, "group_id": 1})
        if response.status_code != 200:
            raise ValueError(str(response.json()))
        assert response.status_code == 200
        response = client.post("/api/target",
                    json={"name": "Not in Search result 2", "description": "Test Description",
                          "target_type": TargetType.user, "group_id": 0})
        if response.status_code != 200:
            raise ValueError(str(response.json()))
        assert response.status_code == 200

        # Make a GET request to the endpoint
        response = client.get("/api/target", params={"name": "Test Target"})

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
    def test_update_target(self):
        # find the target in previous test
        target = target_service.find_one_by_name("Test Target 2")

        # Make a PUT request to the endpoint
        response = client.put(f"/api/target/{target.id}", json={"name": "Updated Target",
                                                                "description": "Updated Description",
                                                                "target_type": TargetType.group,
                                                                "group_id": 1})

        # Assert the response status code
        assert response.status_code == 200

        # Assert the response JSON data
        data = response.json()
        assert "name" in data
        assert "description" in data
        assert "created_at" in data
        assert "updated_at" in data

        # You can also assert against specific values if needed
        assert data["name"] == "Updated Target"

        # Make duplicate name return 400
        response = client.put(f"/api/target/{target.id}", json={"name": "Updated Target",
                                                                "description": "Updated Description",
                                                                "target_type": TargetType.group,
                                                                "group_id": 1})
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "data" in data

    @pytest.mark.run(order=15)
    def test_delete_target(self):
        # create a target to delete
        response = client.post("/api/target",
                               json={"name": "deleted target",
                                     "description": "Test Description",
                                     "target_type": TargetType.group, "group_id": 1}).json()

        # Make a DELETE request to the endpoint
        response = client.delete(f"/api/target/{response['id']}")

        # Assert the response status code
        assert response.status_code == 200

        # Assert the response JSON data
        data = response.json()
        assert "name" in data
        assert "description" in data
        assert "created_at" in data
        assert "updated_at" in data

        # You can also assert against specific values if needed
        assert data["name"] == "deleted target"
        assert data["deleted_at"] is not None

    @pytest.mark.run(order=16)
    def test_create_target_for_process(self):
        staff_group = group_service.find_one_by_name("staff group")
        leader_group = group_service.find_one_by_name("leader group")
        response = client.post("/api/target",
                               json={"name": "staff group", "description": "Test Description",
                                     "target_type": TargetType.group, "group_id": staff_group.id})
        assert response.status_code == 200
        response = client.post("/api/target",
                               json={"name": "leader group", "description": "Test Description",
                                     "target_type": TargetType.group, "group_id": leader_group.id})
        assert response.status_code == 200
