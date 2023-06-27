from pprint import pprint

import pytest

from app.infrastructure.factory_bot.setup_test import counter
from app.infrastructure.factory_bot.user import create_or_get_normal_user
from app.infrastructure.http.fastapi_adapter.group import group_service
from app.pkgs.api_client import client


class TestGroupAPI:

    @pytest.mark.run(order=counter.inc())
    def test_create_new_group(self):
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

    @pytest.mark.run(order=counter.inc())
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

    @pytest.mark.run(order=counter.inc())
    def test_search_group(self):
        # let make some other groups to make this test more sense, also inherit the group created from previous test
        response = client.post("/api/group",
                    json={"name": "Test Group 2", "description": "Test Description"})
        assert response.status_code == 200
        response = client.post("/api/group",
                    json={"name": "Not in Search result", "description": "Test Description"})
        assert response.status_code == 200
        response = client.post("/api/group",
                    json={"name": "Not in Search result", "description": "Test Description"})
        assert response.status_code == 200

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

    @pytest.mark.run(order=counter.inc())
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

    @pytest.mark.run(order=counter.inc())
    def test_delete_group(self):
        # create a group to delete
        response = client.post("/api/group",
                               json={"name": "deleted group",
                                     "description": "Test Description"}).json()

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

    @pytest.mark.run(order=counter.inc())
    def test_add_user_to_group(self):
        # create more group for testing process
        client.post("/api/group",
                    json={"name": "staff group", "description": "Test Description"})
        staff_group = group_service.find_one_by_name("staff group")

        client.post("/api/group",
                    json={"name": "leader group", "description": "Test Description"})

        leader_group = group_service.find_one_by_name("leader group")

        # create users for testing process
        staff_1 = create_or_get_normal_user('staff_1@test_mail.com')
        staff_2 = create_or_get_normal_user('staff_2@test_mail.com')
        staff_3 = create_or_get_normal_user('staff_3@test_mail.com')
        leader_1 = create_or_get_normal_user('leader_1@test_mail.com')
        leader_2 = create_or_get_normal_user('leader_2@test_mail.com')

        # add users to group
        response = client.post(f"/api/group/{staff_group.id}/member/{staff_1.id}", json={})
        assert response.status_code == 200
        response = client.post(f"/api/group/{staff_group.id}/member/{staff_2.id}", json={})
        assert response.status_code == 200
        response = client.post(f"/api/group/{staff_group.id}/member/{staff_3.id}", json={})
        assert response.status_code == 200

        response = client.post(f"/api/group/{leader_group.id}/member/{leader_1.id}", json={})
        assert response.status_code == 200
        response = client.post(f"/api/group/{leader_group.id}/member/{leader_2.id}", json={})
        assert response.status_code == 200

        # Assert the response
        response = client.get(f"/api/group/{staff_group.id}")
        assert response.status_code == 200

        # Assert the response JSON data
        data = response.json()
        assert "name" in data
        assert "description" in data
        assert "created_at" in data
        assert "updated_at" in data
        assert "member" in data

        # You can also assert against specific values if needed
        assert len(data["member"]) == 3

        # Make sure the user is added to the group in the database
        updated_group = group_service.find_one(staff_group.id)
        assert len(updated_group.member) == 3

    @pytest.mark.run(order=counter.inc())
    def test_remove_user_from_group(self):
        removal_member = create_or_get_normal_user('removal_member@test_mail.com')

        # find the group in previous test
        staff_group = group_service.find_one_by_name("staff group")
        response = client.post(f"/api/group/{staff_group.id}/member/{removal_member.id}", json={})
        assert response.status_code == 200

        # Make a DELETE request to the endpoint
        response = client.delete(f"/api/group/{staff_group.id}/member/{removal_member.id}")

        # Assert the response status code
        assert response.status_code == 200

        # Assert the response JSON data
        data = response.json()
        assert "name" in data
        assert "description" in data
        assert "created_at" in data
        assert "updated_at" in data
        assert "member" in data

        # You can also assert against specific values if needed
        assert len(data["member"]) == 3

        # Make sure the user is removed from the group in the database
        updated_group = group_service.find_one(staff_group.id)
        assert len(updated_group.member) == 3
