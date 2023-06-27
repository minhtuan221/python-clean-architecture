import pytest

from app.domain.model.process_maker.state_type import StateType
from app.infrastructure.factory_bot.setup_test import counter
from app.infrastructure.http.fastapi_adapter.process_maker.action import action_service
from app.infrastructure.http.fastapi_adapter.process_maker.activity import activity_service
from app.pkgs.api_client import client
from app.infrastructure.http.fastapi_adapter.process_maker.process import process_service


class TestProcessAPI:

    @pytest.fixture
    @pytest.mark.run(order=301)
    def test_new_process(self):
        # Make a POST request to the endpoint
        response = client.post("/api/process",
                               json={"name": f"Test Process {counter.inc()}",
                                     "description": "Test Description"})

        # Assert the response status code
        assert response.status_code == 200

        # Assert the response JSON data
        data = response.json()
        assert "name" in data
        assert "description" in data
        assert "created_at" in data
        assert "updated_at" in data

        # You can also assert against specific values if needed
        assert data["name"] == f"Test Process {counter.value}"
        new_process = process_service.find_one(data['id'])
        yield new_process

    @pytest.mark.run(order=302)
    def test_find_one_process(self, test_new_process):
        # Make a GET request to the endpoint
        response = client.get(f"/api/process/{test_new_process.id}")

        # Assert the response status code
        assert response.status_code == 200

        # Assert the response JSON data
        data = response.json()
        assert "name" in data
        assert "description" in data
        assert "created_at" in data
        assert "updated_at" in data

        # You can also assert against specific values if needed
        assert data["name"] == "Test Process 1"

    @pytest.mark.run(order=303)
    def test_search_process(self):
        # let make some other process to make this test more sense, also inherit the process created from previous test
        response = client.post("/api/process",
                               json={"name": "Test Process show in result",
                                     "description": "Test Description"})
        assert response.status_code == 200
        response = client.post("/api/process",
                               json={"name": "Not in Search result 1",
                                     "description": "Test Description"})
        assert response.status_code == 200
        response = client.post("/api/process",
                               json={"name": "Not in Search result 2",
                                     "description": "Test Description"})
        assert response.status_code == 200

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

    @pytest.mark.run(order=304)
    def test_update_process(self):
        # find the process in previous test
        response = client.post("/api/process",
                               json={"name": "Process not updated yet",
                                     "description": "Test Description"})
        assert response.status_code == 200
        data = response.json()
        process_id = data['id']

        # Make a PUT request to the endpoint
        response = client.put(f"/api/process/{process_id}", json={"name": "Updated Process",
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
        response = client.put(f"/api/process/{process_id}", json={"name": "Updated Process",
                                                                  "description": "Updated Description"})
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "data" in data

    @pytest.mark.run(order=305)
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

    @pytest.fixture
    @pytest.mark.run(order=306)
    def test_add_state_to_process(self, test_new_process):
        process_id = test_new_process.id

        # add state to process
        response = client.post(f"/api/process/{process_id}/state",
                               json={"name": "start point",
                                     "description": "Test Description",
                                     'state_type': 'start'})

        # Assert the response status code
        assert response.status_code == 200

        # Assert the response JSON data
        data = response.json()
        state_id = data['id']
        yield process_service.find_state_on_process(process_id, state_id)

    @pytest.mark.run(order=306)
    def test_add_duplicate_state_to_process(self, test_new_process, test_add_state_to_process):
        process_id = test_new_process.id

        # return 400 if duplicate state name
        response = client.post(f"/api/process/{process_id}/state",
                               json={"name": "start point",
                                     "description": "Test Description",
                                     'state_type': 'start'})

        # Assert the response status code
        assert response.status_code == 400

    @pytest.mark.run(order=306)
    def test_update_state_to_process(self, test_new_process, test_add_state_to_process):
        process_id = test_new_process.id
        state_id = test_add_state_to_process.id
        # update state to process
        response = client.put(f"/api/process/{process_id}/state/{state_id}",
                              json={"name": "updated state point",
                                    "description": "Test updated Description"})

        # Assert the response status code
        assert response.status_code == 200

        # Assert the response JSON data
        data = response.json()
        assert data['name'] == "updated state point"
        assert data['description'] == "Test updated Description"

    @pytest.mark.run(order=306)
    def test_update_dup_state_to_process(self, test_new_process, test_add_state_to_process):
        process_id = test_new_process.id
        # add state to process
        response = client.post(f"/api/process/{process_id}/state",
                               json={"name": "second point",
                                     "description": "Test Description",
                                     'state_type': 'start'})

        # Assert the response status code
        assert response.status_code == 200

        # Assert the response JSON data
        data = response.json()
        state_id = data['id']

        # update duplicate state
        response = client.put(f"/api/process/{process_id}/state/{state_id}",
                              json={"name": "start point",
                                    "description": "Test updated Description"})

        # Assert the response status code
        assert response.status_code == 400

    @pytest.mark.run(order=306)
    def test_remove_state_from_process(self, test_new_process, test_add_state_to_process):
        process_id = test_new_process.id
        state_id = test_add_state_to_process.id

        # remove state from process
        response = client.delete(f"/api/process/{process_id}/state/{state_id}", )

        # Assert the response status code
        assert response.status_code == 200
        data = response.json()
        assert data['deleted_at'] is not None

    @pytest.fixture
    @pytest.mark.run(order=306)
    def test_add_route_to_process(self, test_new_process, test_add_state_to_process):
        process_id = test_new_process.id
        # add state to process
        response = client.post(f"/api/process/{process_id}/state",
                               json={"name": "second point",
                                     "description": "Test Description",
                                     'state_type': 'start'})

        # Assert the response status code
        assert response.status_code == 200

        # Assert the response JSON data
        data = response.json()
        second_state_id = data['id']

        response = client.post(
            f"/api/process/{process_id}/route",
            json={"current_state_id": test_add_state_to_process.id,
                  "next_state_id": second_state_id})
        assert response.status_code == 200
        data = response.json()
        yield process_service.find_route_on_process(process_id, data['id'])

    @pytest.mark.run(order=306)
    def test_add_dup_route_to_process(self, test_new_process, test_add_route_to_process):
        process_id = test_new_process.id

        response = client.post(
            f"/api/process/{process_id}/route",
            json={"current_state_id": test_add_route_to_process.current_state_id,
                  "next_state_id": test_add_route_to_process.next_state_id})
        assert response.status_code == 400

    @pytest.mark.run(order=306)
    def test_add_revert_route_to_process(self, test_new_process, test_add_route_to_process):
        process_id = test_new_process.id

        response = client.post(
            f"/api/process/{process_id}/route",
            json={"current_state_id": test_add_route_to_process.next_state_id,
                  "next_state_id": test_add_route_to_process.current_state_id})
        assert response.status_code == 200

    @pytest.mark.run(order=306)
    def test_add_no_next_state_route_to_process(self, test_new_process, test_add_route_to_process):
        process_id = test_new_process.id

        response = client.post(
            f"/api/process/{process_id}/route",
            json={"current_state_id": test_add_route_to_process.next_state_id,
                  "next_state_id": 0})
        assert response.status_code == 200

    @pytest.mark.run(order=306)
    def test_remove_route_from_process(self, test_new_process, test_add_route_to_process):
        process_id = test_new_process.id

        response = client.delete(
            f"/api/process/{process_id}/route/{test_add_route_to_process.id}")
        assert response.status_code == 200
        data = response.json()
        assert data['deleted_at'] is not None

    @pytest.mark.run(order=307)
    def test_create_completed_process(self):
        # Make a POST request to the endpoint
        response = client.post("/api/process",
                               json={"name": "Test Process Workflow",
                                     "description": "Test Description"})

        # Assert the response status code
        assert response.status_code == 200

        # Assert the response JSON data
        data = response.json()
        assert "name" in data
        assert "description" in data
        assert "created_at" in data
        assert "updated_at" in data

        # You can also assert against specific values if needed
        assert data["name"] == "Test Process Workflow"

    @pytest.mark.run(order=308)
    def test_add_state_to_completed_process(self):
        # get Test Process from previous test
        process = process_service.find_one_by_name("Test Process Workflow")

        # add state to process
        response = client.post(f"/api/process/{process.id}/state",
                               json={"name": "start point",
                                     "description": "Test Description",
                                     'state_type': 'start'})

        # Assert the response status code
        assert response.status_code == 200

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
        response = client.post(f"/api/process/{process.id}/state",
                               json={"name": "request for approve",
                                     "description": "Test Description",
                                     'state_type': StateType.normal})
        assert response.status_code == 200
        response = client.post(f"/api/process/{process.id}/state",
                               json={"name": "done",
                                     "description": "Test Description",
                                     'state_type': StateType.complete})
        assert response.status_code == 200
        response = client.post(f"/api/process/{process.id}/state",
                               json={"name": "denied",
                                     "description": "Test Description",
                                     'state_type': StateType.complete})
        assert response.status_code == 200

    @pytest.mark.run(order=309)
    def test_add_route_to_completed_process(self):
        # get Test Process from previous test
        process = process_service.find_one_by_name("Test Process Workflow")

        start_point = process_service.find_state_on_process_by_name(process.id, 'start point')
        request_for_approve = process_service.find_state_on_process_by_name(process.id,
                                                                            'request for approve')
        done_state = process_service.find_state_on_process_by_name(process.id, 'done')
        denied_state = process_service.find_state_on_process_by_name(process.id, 'denied')

        # add activity to state
        add_note_when_edit = activity_service.find_one_by_name("add note when edit")
        send_email_leader = activity_service.find_one_by_name("send email leader")
        send_email_staff = activity_service.find_one_by_name("send email staff")

        # notify leader about the new request
        response = client.post(
            f"/api/process/{process.id}/state/{request_for_approve.id}/activity/{send_email_leader.id}")
        assert response.status_code == 200
        # notify staff that their request has been approved
        response = client.post(
            f"/api/process/{process.id}/state/{done_state.id}/activity/{send_email_staff.id}")
        assert response.status_code == 200
        # notify staff that their request has been denied
        response = client.post(
            f"/api/process/{process.id}/state/{denied_state.id}/activity/{send_email_staff.id}")
        assert response.status_code == 200

        # add route to process
        response = client.post(f"/api/process/{process.id}/route",
                               json={"current_state_id": start_point.id,
                                     "next_state_id": request_for_approve.id})

        # Assert the response status code
        assert response.status_code == 200
        start_point_to_request_for_approve = process_service.find_route_on_process(process.id,
                                                                                   response.json()[
                                                                                       'id'])

        # Assert the response JSON data
        data = response.json()

        # You can also assert against specific values if needed
        assert data["current_state_id"] == start_point.id
        assert data['next_state_id'] == request_for_approve.id

        # make more route for further testing
        response = client.post(f"/api/process/{process.id}/route",
                               json={"current_state_id": request_for_approve.id,
                                     "next_state_id": done_state.id})
        assert response.status_code == 200
        request_for_approve_to_done = process_service.find_route_on_process(process.id,
                                                                            response.json()['id'])

        response = client.post(f"/api/process/{process.id}/route",
                               json={"current_state_id": request_for_approve.id,
                                     "next_state_id": denied_state.id})
        assert response.status_code == 200
        request_for_approve_to_denied = process_service.find_route_on_process(process.id,
                                                                              response.json()['id'])
        response = client.post(f"/api/process/{process.id}/route",
                               json={"current_state_id": request_for_approve.id,
                                     "next_state_id": start_point.id})
        assert response.status_code == 200
        request_for_approve_to_start_point = process_service.find_route_on_process(process.id,
                                                                                   response.json()[
                                                                                       'id'])
        response = client.post(f"/api/process/{process.id}/route",
                               json={"current_state_id": start_point.id,
                                     "next_state_id": 0})
        assert response.status_code == 200
        start_point_to_itself = process_service.find_route_on_process(process.id,
                                                                      response.json()['id'])

        # add activity to route
        # notify that the request has been changed by staff (requester)
        response = client.post(
            f"/api/process/{process.id}/route/{start_point_to_itself.id}/activity/{add_note_when_edit.id}")
        assert response.status_code == 200

        # get all actions:
        edit_act = action_service.find_one_by_name('edit request')
        cancel_act = action_service.find_one_by_name('cancel request')
        raise_act = action_service.find_one_by_name('raise request')
        approve_act = action_service.find_one_by_name('approve request')
        deny_act = action_service.find_one_by_name('deny request')
        reject_act = action_service.find_one_by_name('reject request')

        # add action to route
        # allow staff edit their request at start point
        response = client.post(
            f"/api/process/{process.id}/route/{start_point_to_itself.id}/action/{edit_act.id}")
        assert response.status_code == 200
        # allow staff cancel request
        response = client.post(
            f"/api/process/{process.id}/route/{request_for_approve_to_start_point.id}/action/{cancel_act.id}")
        assert response.status_code == 200
        # allow staff raise request to leader
        response = client.post(
            f"/api/process/{process.id}/route/{start_point_to_request_for_approve.id}/action/{raise_act.id}")
        assert response.status_code == 200
        # allow leader approve request
        response = client.post(
            f"/api/process/{process.id}/route/{request_for_approve_to_done.id}/action/{approve_act.id}")
        assert response.status_code == 200
        # allow leader deny request
        response = client.post(
            f"/api/process/{process.id}/route/{request_for_approve_to_denied.id}/action/{deny_act.id}")
        assert response.status_code == 200
        # allow leader reject request
        response = client.post(
            f"/api/process/{process.id}/route/{request_for_approve_to_start_point.id}/action/{reject_act.id}")
        assert response.status_code == 200

        complete_process = process_service.find_one_by_name("Test Process Workflow")

        assert len(complete_process.to_json()['state']) == 4
