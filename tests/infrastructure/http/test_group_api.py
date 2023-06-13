import pytest

from app.infrastructure.http.fastapi_adapter.group import group_service
from app.pkgs.api_client import client


class TestGroupAPI:

    @pytest.mark.run(order=1)
    def test_create_new_group(self):
        print('\ntest group api')
        # Make a POST request to the endpoint
        response = client.post("/api/group",
                               json={"name": "Test Group", "description": "Test Description"})

        # Assert the response status code
        assert response.status_code == 200

        # Assert the response JSON data
        data = response.json()
        assert "name" in data
        assert "description" in data
        assert "created_at" in data
        assert "updated_at" in data

        # You can also assert against specific values if needed
        assert data["name"] == "Test Group"

    @pytest.mark.run(order=2)
    def test_find_one_group(self):
        # find the group in previous test
        group = group_service.find_one_by_name("Test Group")

        # Make a GET request to the endpoint
        response = client.get(f"/api/group/{group.id}")

        # Assert the response status code
        assert response.status_code == 200

        # Assert the response JSON data
        data = response.json()
        assert "name" in data
        assert "description" in data
        assert "created_at" in data
        assert "updated_at" in data

        # You can also assert against specific values if needed
        assert data["name"] == "Test Group"

    @pytest.mark.run(order=3)
    def test_search_group(self):
        # let make some other groups to make this test more sense, also inherit the group created from previous test
        client.post("/api/group",
                    json={"name": "Test Group 2", "description": "Test Description"})
        client.post("/api/group",
                    json={"name": "Not in Search result", "description": "Test Description"})
        client.post("/api/group",
                    json={"name": "Not in Search result", "description": "Test Description"})

        # Make a GET request to the endpoint
        response = client.get("/api/group", params={"name": "Test Group"})

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

    @pytest.mark.run(order=4)
    def test_update_group(self):
        # find the group in previous test
        group = group_service.find_one_by_name("Test Group 2")

        # Make a PUT request to the endpoint
        response = client.put(f"/api/group/{group.id}", json={"name": "Updated Group",
                                                             "description": "Updated Description"})

        # Assert the response status code
        assert response.status_code == 200

        # Assert the response JSON data
        data = response.json()
        assert "name" in data
        assert "description" in data
        assert "created_at" in data
        assert "updated_at" in data

        # You can also assert against specific values if needed
        assert data["name"] == "Updated Group"

        # Make duplicate name return 400
        response = client.put(f"/api/group/{group.id}", json={"name": "Updated Group",
                                                             "description": "Updated Description"})
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "data" in data

    @pytest.mark.run(order=5)
    def test_delete_group(self):
        # create a group to delete
        response = client.post("/api/group",
                               json={"name": "deleted group", "description": "Test Description"}).json()

        # Make a DELETE request to the endpoint
        response = client.delete(f"/api/group/{response['id']}")

        # Assert the response status code
        assert response.status_code == 200

        # Assert the response JSON data
        data = response.json()
        assert "name" in data
        assert "description" in data
        assert "created_at" in data
        assert "updated_at" in data

        # You can also assert against specific values if needed
        assert data["name"] == "deleted group"
        assert data["deleted_at"] is not None
