import pytest

from app.domain.model.process_maker.activity_type import ActivityType
from app.infrastructure.factory_bot.setup_test import counter
from app.infrastructure.http.fastapi_adapter.process_maker.target import target_service
from app.pkgs.api_client import client
from app.infrastructure.http.fastapi_adapter.process_maker.activity import activity_service

test_order = 20


class TestActivityAPI:

    @pytest.mark.run(order=counter.inc())
    def test_create_new_activity(self):
        # Make a POST request to the endpoint
        response = client.post("/api/activity",
                               json={"name": "Test Activity", "description": "Test Description",
                                     "activity_type": ActivityType.add_note})

        # Assert the response status code
        assert response.status_code == 200

        # Assert the response JSON data
        data = response.json()
        assert "name" in data
        assert "description" in data
        assert "activity_type" in data
        assert "created_at" in data
        assert "updated_at" in data

        # You can also assert against specific values if needed
        assert data["name"] == "Test Activity"
        assert data["description"] == "Test Description"
        assert data["activity_type"] == ActivityType.add_note

    @pytest.mark.run(order=counter.inc())
    def test_find_one_activity(self):
        # find the activity in the previous test
        activity = activity_service.find_one_by_name("Test Activity")

        # Make a GET request to the endpoint
        response = client.get(f"/api/activity/{activity.id}")

        # Assert the response status code
        assert response.status_code == 200

        # Assert the response JSON data
        data = response.json()
        assert "name" in data
        assert "description" in data
        assert "activity_type" in data
        assert "created_at" in data
        assert "updated_at" in data

        # You can also assert against specific values if needed
        assert data["name"] == "Test Activity"
        assert data["description"] == "Test Description"
        assert data["activity_type"] == ActivityType.add_note

    @pytest.mark.run(order=counter.inc())
    def test_search_activity(self):
        # let's make some other activities to make this test more meaningful,
        # also inherit the activity created from the previous test
        client.post("/api/activity",
                    json={"name": "Test Activity 2", "description": "Test Description",
                          "activity_type": ActivityType.remove_stakeholder})
        client.post("/api/activity",
                    json={"name": "Not in Search result", "description": "Test Description",
                          "activity_type": ActivityType.add_note})
        client.post("/api/activity",
                    json={"name": "Not in Search result", "description": "Test Description",
                          "activity_type": ActivityType.remove_stakeholder})

        # Make a GET request to the endpoint
        response = client.get("/api/activity", params={"name": "Test Activity"})

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

    @pytest.mark.run(order=counter.inc())
    def test_update_activity(self):
        # find the activity in the previous test
        activity = activity_service.find_one_by_name("Test Activity 2")

        # Make a PUT request to the endpoint
        response = client.put(f"/api/activity/{activity.id}", json={"name": "Updated Activity",
                                                                   "description": "Updated Description",
                                                                   "activity_type": ActivityType.send_email})

        # Assert the response status code
        assert response.status_code == 200

        # Assert the response JSON data
        data = response.json()
        assert "name" in data
        assert "description" in data
        assert "activity_type" in data
        assert "created_at" in data
        assert "updated_at" in data

        # You can also assert against specific values if needed
        assert data["name"] == "Updated Activity"
        assert data["description"] == "Updated Description"
        assert data["activity_type"] == ActivityType.send_email

        # Make duplicate name return 400
        response = client.put(f"/api/activity/{activity.id}", json={"name": "Updated Activity",
                                                                   "description": "Updated Description",
                                                                   "activity_type": ActivityType.send_email})
        assert response.status_code == 400
        data = response.json()
        assert "error" in data
        assert "data" in data

    @pytest.mark.run(order=counter.inc())
    def test_delete_activity(self):
        # create an activity to delete
        response = client.post("/api/activity",
                               json={"name": "Deleted Activity",
                                     "description": "Test Description",
                                     "activity_type": ActivityType.send_email}).json()

        # Make a DELETE request to the endpoint
        response = client.delete(f"/api/activity/{response['id']}")

        # Assert the response status code
        assert response.status_code == 200

        # Assert the response JSON data
        data = response.json()
        assert "name" in data
        assert "description" in data
        assert "activity_type" in data
        assert "created_at" in data
        assert "updated_at" in data

        # You can also assert against specific values if needed
        assert data["name"] == "Deleted Activity"
        assert data["description"] == "Test Description"
        assert data["activity_type"] == ActivityType.send_email
        assert data["deleted_at"] is not None

    @pytest.mark.run(order=counter.inc())
    def test_create_activity_for_completed_process(self):
        response = client.post("/api/activity",
                               json={"name": "add note when edit",
                                     "description": "add note if change request information",
                                     "activity_type": ActivityType.add_note})
        assert response.status_code == 200
        add_note_when_edit = activity_service.find_one(response.json()['id'])
        response = client.post("/api/activity",
                               json={"name": "send email leader",
                                     "description": "send email notify leader",
                                     "activity_type": ActivityType.send_email})
        assert response.status_code == 200
        send_email_leader = activity_service.find_one(response.json()['id'])
        response = client.post("/api/activity",
                               json={"name": "send email staff",
                                     "description": "send email notify staff",
                                     "activity_type": ActivityType.send_email})
        assert response.status_code == 200
        send_email_staff = activity_service.find_one(response.json()['id'])

        # add target to activity
        staff_group = target_service.find_one_by_name('staff group')
        leader_group = target_service.find_one_by_name('leader group')
        response = client.post(f"/api/activity/{add_note_when_edit.id}/target/{staff_group.id}")
        assert response.status_code == 200
        response = client.post(f"/api/activity/{send_email_staff.id}/target/{staff_group.id}")
        assert response.status_code == 200
        response = client.post(f"/api/activity/{send_email_leader.id}/target/{leader_group.id}")
        assert response.status_code == 200
