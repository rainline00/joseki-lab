"""
Contract tests for Trees API endpoints.

Tests API contract based on OpenAPI specification.
Phase 3.1: TDD Red phase - tests should fail until implementation.
"""

import uuid

import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

# 平手初期局面の SFEN
INITIAL_SFEN = "lnsgkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL b -"


@pytest.fixture
def api_client():
    """DRF APIClient fixture"""
    return APIClient()


@pytest.mark.django_db
class TestTreesCreateContract:
    """T005: Contract test for POST /trees (201, 400)"""

    def test_create_tree_success(self, api_client):
        """POST /trees should return 201 with tree data including root_node"""
        url = "/api/v1/trees/"
        data = {"name": "矢倉", "description": "矢倉戦法の定跡集"}

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()

        # Required fields check
        assert "id" in response_data
        assert response_data["name"] == "矢倉"
        assert response_data["description"] == "矢倉戦法の定跡集"
        assert response_data["node_count"] == 1
        assert response_data["is_deleted"] is False
        assert response_data["deleted_at"] is None
        assert "created_at" in response_data
        assert "updated_at" in response_data

        # Root node should be included
        assert "root_node" in response_data
        root_node = response_data["root_node"]
        assert root_node["sfen"] == INITIAL_SFEN
        assert root_node["ply"] == 0
        assert root_node["is_root"] is True

    def test_create_tree_minimal(self, api_client):
        """POST /trees with only name should succeed"""
        url = "/api/v1/trees/"
        data = {"name": "居飛車"}

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()
        assert response_data["name"] == "居飛車"
        assert response_data["description"] == ""


@pytest.mark.django_db
class TestTreesCreateValidation:
    """T006: Contract test for POST /trees with empty name (400)"""

    def test_create_tree_empty_name(self, api_client):
        """POST /trees with empty name should return 400"""
        url = "/api/v1/trees/"
        data = {"name": "", "description": "説明"}

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response_data = response.json()
        assert "name" in response_data or "error" in response_data

    def test_create_tree_missing_name(self, api_client):
        """POST /trees without name should return 400"""
        url = "/api/v1/trees/"
        data = {"description": "説明のみ"}

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestTreesListContract:
    """T007: Contract test for GET /trees (200)"""

    def test_list_trees_empty(self, api_client):
        """GET /trees with no trees should return empty list"""
        url = "/api/v1/trees/"

        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_list_trees_with_data(self, api_client):
        """GET /trees should return list of trees with summary info"""
        # Create a tree first
        create_url = "/api/v1/trees/"
        api_client.post(create_url, {"name": "矢倉"}, format="json")
        api_client.post(create_url, {"name": "四間飛車"}, format="json")

        response = api_client.get(create_url)

        assert response.status_code == status.HTTP_200_OK
        trees = response.json()
        assert len(trees) == 2

        # Summary fields check (no root_node in list view)
        for tree in trees:
            assert "id" in tree
            assert "name" in tree
            assert "node_count" in tree
            assert "created_at" in tree
            assert "updated_at" in tree


@pytest.mark.django_db
class TestTreesRetrieveContract:
    """T008: Contract test for GET /trees/{id} (200, 404)"""

    def test_get_tree_success(self, api_client):
        """GET /trees/{id} should return tree detail with root_node"""
        # Create a tree first
        create_url = "/api/v1/trees/"
        create_response = api_client.post(
            create_url, {"name": "中飛車"}, format="json"
        )
        tree_id = create_response.json()["id"]

        url = f"/api/v1/trees/{tree_id}/"
        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["id"] == tree_id
        assert response_data["name"] == "中飛車"
        assert "root_node" in response_data
        assert response_data["root_node"]["sfen"] == INITIAL_SFEN

    def test_get_tree_not_found(self, api_client):
        """GET /trees/{id} with invalid id should return 404"""
        fake_id = str(uuid.uuid4())
        url = f"/api/v1/trees/{fake_id}/"

        response = api_client.get(url)

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestTreesUpdateContract:
    """T009: Contract test for PATCH /trees/{id} (200, 404)"""

    def test_update_tree_success(self, api_client):
        """PATCH /trees/{id} should update tree and return updated data"""
        # Create a tree first
        create_url = "/api/v1/trees/"
        create_response = api_client.post(
            create_url, {"name": "オリジナル"}, format="json"
        )
        tree_id = create_response.json()["id"]

        url = f"/api/v1/trees/{tree_id}/"
        update_data = {"name": "更新後の名前", "description": "新しい説明"}

        response = api_client.patch(url, update_data, format="json")

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["name"] == "更新後の名前"
        assert response_data["description"] == "新しい説明"

    def test_update_tree_partial(self, api_client):
        """PATCH /trees/{id} with partial data should work"""
        # Create a tree first
        create_url = "/api/v1/trees/"
        create_response = api_client.post(
            create_url,
            {"name": "元の名前", "description": "元の説明"},
            format="json",
        )
        tree_id = create_response.json()["id"]

        url = f"/api/v1/trees/{tree_id}/"
        update_data = {"name": "名前のみ更新"}

        response = api_client.patch(url, update_data, format="json")

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["name"] == "名前のみ更新"
        assert response_data["description"] == "元の説明"  # 変更なし

    def test_update_tree_not_found(self, api_client):
        """PATCH /trees/{id} with invalid id should return 404"""
        fake_id = str(uuid.uuid4())
        url = f"/api/v1/trees/{fake_id}/"
        update_data = {"name": "更新"}

        response = api_client.patch(url, update_data, format="json")

        assert response.status_code == status.HTTP_404_NOT_FOUND
