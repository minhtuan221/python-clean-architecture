import pytest

from app.cmd.http import app
from app.domain.model import Process
from app.infrastructure.factory_bot.user import gen_token_for_normal_user
from app.infrastructure.http.fastapi_adapter.process import process_service
from app.pkgs.api_client import APIClient

client = APIClient(app, gen_token_for_normal_user())


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
        response = client.get(f"/api/process")

        # Assert the response status code
        assert response.status_code == 200

        # Assert the response JSON data
        assert "data" in response.json()
        data = response.json()["data"]
        assert len(data) == 2
