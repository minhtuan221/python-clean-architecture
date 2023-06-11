import pytest

from app.pkgs.api_client import client
from app.infrastructure.http.fastapi_adapter.process_maker.process import process_service


class TestProcessAPI:

    @pytest.mark.run(order=1)
    def test_create_new_process(self):
        # Make a POST request to the endpoint
        response = client.post("/api/process", json={"name": "Test Process", "description": "Test Description"})

        # Assert the response status code
        assert response.status_code == 200

        # Assert the response JSON data
        data = response.json()
        assert "name" in data
        assert "description" in data
        assert "created_at" in data
        assert "updated_at" in data

        # You can also assert against specific values if needed
        assert data["name"] == "Test Process"

    @pytest.mark.run(order=2)
    def test_find_one_process(self):
        # Create a test process
        process = process_service.create(name="Test Process 2", description="Test Description")

        # Make a GET request to the endpoint
        response = client.get(f"/api/process/{process.id}")

        # Assert the response status code
        assert response.status_code == 200

        # Assert the response JSON data
        data = response.json()
        assert "name" in data
        assert "description" in data
        assert "created_at" in data
        assert "updated_at" in data

        # You can also assert against specific values if needed
        assert data["name"] == "Test Process 2"

    @pytest.mark.run(order=3)
    def test_search_process(self):
        # Make a GET request to the endpoint
        response = client.get("/api/process", params={"name": "Test Process"})

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
    def test_update_process(self):
        # Create a test process
        process = process_service.create(name="Test Process 3", description="Test Description")

        # Make a PUT request to the endpoint
        response = client.put(f"/api/process/{process.id}", json={"name": "Updated Process", "description": "Updated Description"})

        # Assert the response status code
        assert response.status_code == 200

        # Assert the response JSON data
        data = response.json()
        assert "name" in data
        assert "description" in data
        assert "created_at" in data
        assert "updated_at" in data

        # You can also assert against specific values if needed
        assert data["name"] == "Updated Process"

        # Make duplicate name return 400
        response = client.put(f"/api/process/{process.id}", json={"name": "Updated Process",
                                                                  "description": "Updated Description"})
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "data" in data

    @pytest.mark.run(order=5)
    def test_delete_process(self):
        # Create a test process
        process = process_service.create(name="Test Process 4", description="Test Description")

        # Make a DELETE request to the endpoint
        response = client.delete(f"/api/process/{process.id}")

        # Assert the response status code
        assert response.status_code == 200

        # Assert the response JSON data
        data = response.json()
        assert "name" in data
        assert "description" in data
        assert "created_at" in data
        assert "updated_at" in data

        # You can also assert against specific values if needed
        assert data["name"] == "Test Process 4"
        assert data["deleted_at"] is not None
