from pprint import pprint

import pytest

from app.domain.model.process_maker.state_type import StateType
from app.pkgs.api_client import client
from app.infrastructure.http.fastapi_adapter.process_maker.process import process_service


class TestProcessAPI:

    @pytest.mark.run(order=31)
    def test_create_new_process(self):
        print('\ntest process api')
        # Make a POST request to the endpoint
        response = client.post("/api/process",
                               json={"name": "Test Process", "description": "Test Description"})

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

    @pytest.mark.run(order=32)
    def test_find_one_process(self):
        # find the process in previous test
        processes = process_service.search("Test Process")

        # Make a GET request to the endpoint
        response = client.get(f"/api/process/{processes[0].id}")

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

    @pytest.mark.run(order=33)
    def test_search_process(self):
        # let make some other process to make this test more sense, also inherit the process created from previous test
        client.post("/api/process",
                    json={"name": "Test Process 2", "description": "Test Description"})
        client.post("/api/process",
                    json={"name": "Not in Search result", "description": "Test Description"})
        client.post("/api/process",
                    json={"name": "Not in Search result", "description": "Test Description"})

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

    @pytest.mark.run(order=34)
    def test_update_process(self):
        # find the process in previous test
        process = process_service.find_one_by_name("Test Process 2")

        # Make a PUT request to the endpoint
        response = client.put(f"/api/process/{process.id}", json={"name": "Updated Process",
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
        assert data["name"] == "Updated Process"

        # Make duplicate name return 400
        response = client.put(f"/api/process/{process.id}", json={"name": "Updated Process",
                                                                  "description": "Updated Description"})
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "data" in data

    @pytest.mark.run(order=35)
    def test_delete_process(self):
        # create a process to delete
        response = client.post("/api/process",
                               json={"name": "deleted process",
                                     "description": "Test Description"}).json()

        # Make a DELETE request to the endpoint
        response = client.delete(f"/api/process/{response['id']}")

        # Assert the response status code
        assert response.status_code == 200

        # Assert the response JSON data
        data = response.json()
        assert "name" in data
        assert "description" in data
        assert "created_at" in data
        assert "updated_at" in data

        # You can also assert against specific values if needed
        assert data["name"] == "deleted process"
        assert data["deleted_at"] is not None

    @pytest.mark.run(order=36)
    def test_add_state_to_process(self):
        # get Test Process from previous test
        process = process_service.find_one_by_name("Test Process")

        # add state to process
        response = client.post(f"/api/process/{process.id}/state",
                               json={"name": "start point",
                                     "description": "Test Description",
                                     'state_type': 'start'})

        # Assert the response status code
        assert response.status_code == 200

        # pprint(response.json())

        # Assert the response JSON data
        data = response.json()
        assert "name" in data
        assert "description" in data
        assert "created_at" in data
        assert "updated_at" in data

        # You can also assert against specific values if needed
        assert data["name"] == "start point"
        assert data['state_type'] == 'start'

        # add more state for further testing
        client.post(f"/api/process/{process.id}/state",
                    json={"name": "request to approve",
                          "description": "Test Description",
                          'state_type': StateType.normal})
        client.post(f"/api/process/{process.id}/state",
                    json={"name": "done",
                          "description": "Test Description",
                          'state_type': StateType.complete})
        client.post(f"/api/process/{process.id}/state",
                    json={"name": "denied",
                          "description": "Test Description",
                          'state_type': StateType.complete})

    @pytest.mark.run(order=37)
    def test_add_route_to_process(self):
        # get Test Process from previous test
        process = process_service.find_one_by_name("Test Process")

        start_point = process_service.find_state_on_process_by_name(process.id, 'start point')
        request_to_approve = process_service.find_state_on_process_by_name(process.id,
                                                                           'request to approve')
        done_state = process_service.find_state_on_process_by_name(process.id, 'done')
        denied_state = process_service.find_state_on_process_by_name(process.id, 'denied')

        # add state to process
        response = client.post(f"/api/process/{process.id}/route",
                               json={"current_state_id": start_point.id,
                                     "next_state_id": request_to_approve.id})

        # Assert the response status code
        assert response.status_code == 200

        # Assert the response JSON data
        data = response.json()

        # You can also assert against specific values if needed
        assert data["current_state_id"] == start_point.id
        assert data['next_state_id'] == request_to_approve.id

        # make more route for further testing
        response = client.post(f"/api/process/{process.id}/route",
                    json={"current_state_id": request_to_approve.id,
                          "next_state_id": done_state.id})
        assert response.status_code == 200
        response = client.post(f"/api/process/{process.id}/route",
                    json={"current_state_id": request_to_approve.id,
                          "next_state_id": denied_state.id})
        assert response.status_code == 200
        response = client.post(f"/api/process/{process.id}/route",
                    json={"current_state_id": request_to_approve.id,
                          "next_state_id": start_point.id})
        assert response.status_code == 200
        response = client.post(f"/api/process/{process.id}/route",
                    json={"current_state_id": request_to_approve.id,
                          "next_state_id": 0})
        assert response.status_code == 200
