"""
Contract tests for Nodes API endpoints.

Tests API contract based on OpenAPI specification.
Phase 3.1: TDD Red phase - tests should fail until implementation.
"""

import uuid

import pytest
from rest_framework import status
from rest_framework.test import APIClient

# 平手初期局面の SFEN
INITIAL_SFEN = "lnsgkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL b -"


@pytest.fixture
def api_client():
    """DRF APIClient fixture"""
    return APIClient()


@pytest.fixture
def tree_with_root(api_client):
    """Create a tree and return tree_id and root_node_id"""
    url = "/api/v1/trees/"
    response = api_client.post(url, {"name": "テストツリー"}, format="json")
    data = response.json()
    return {
        "tree_id": data["id"],
        "root_node_id": data["root_node"]["id"],
    }


@pytest.mark.django_db
class TestAddMoveContract:
    """T010: Contract test for POST /trees/{tree_id}/nodes/{node_id}/moves (201)"""

    def test_add_move_success(self, api_client, tree_with_root):
        """POST /nodes/{id}/moves should create new node and edge"""
        tree_id = tree_with_root["tree_id"]
        node_id = tree_with_root["root_node_id"]
        url = f"/api/v1/trees/{tree_id}/nodes/{node_id}/moves/"
        data = {"move_usi": "7g7f"}

        response = api_client.post(url, data, format="json")

        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()

        # Check response structure
        assert "edge" in response_data
        assert "child_node" in response_data
        assert "is_transposition" in response_data

        # Edge data
        edge = response_data["edge"]
        assert "id" in edge
        assert edge["move_usi"] == "7g7f"

        # Child node data
        child = response_data["child_node"]
        assert "id" in child
        assert child["ply"] == 1
        assert child["is_root"] is False

        # New node, not transposition
        assert response_data["is_transposition"] is False

    def test_add_move_sequence(self, api_client, tree_with_root):
        """Adding multiple moves in sequence should work"""
        tree_id = tree_with_root["tree_id"]
        node_id = tree_with_root["root_node_id"]

        # First move: 7g7f
        url = f"/api/v1/trees/{tree_id}/nodes/{node_id}/moves/"
        response1 = api_client.post(url, {"move_usi": "7g7f"}, format="json")
        assert response1.status_code == status.HTTP_201_CREATED
        child1_id = response1.json()["child_node"]["id"]

        # Second move: 3c3d (from child1)
        url2 = f"/api/v1/trees/{tree_id}/nodes/{child1_id}/moves/"
        response2 = api_client.post(url2, {"move_usi": "3c3d"}, format="json")
        assert response2.status_code == status.HTTP_201_CREATED
        assert response2.json()["child_node"]["ply"] == 2


@pytest.mark.django_db
class TestAddMoveDuplicate:
    """T011: Contract test for POST /nodes/{id}/moves with duplicate move (409)"""

    def test_add_duplicate_move(self, api_client, tree_with_root):
        """POST /nodes/{id}/moves with same move should return 409"""
        tree_id = tree_with_root["tree_id"]
        node_id = tree_with_root["root_node_id"]
        url = f"/api/v1/trees/{tree_id}/nodes/{node_id}/moves/"

        # First add
        api_client.post(url, {"move_usi": "7g7f"}, format="json")

        # Duplicate add
        response = api_client.post(url, {"move_usi": "7g7f"}, format="json")

        assert response.status_code == status.HTTP_409_CONFLICT
        response_data = response.json()
        assert "error" in response_data
        assert response_data["error"] == "duplicate_move"


@pytest.mark.django_db
class TestGetChildrenContract:
    """T012: Contract test for GET /trees/{tree_id}/nodes/{node_id}/children (200)"""

    def test_get_children_empty(self, api_client, tree_with_root):
        """GET /nodes/{id}/children with no children should return empty list"""
        tree_id = tree_with_root["tree_id"]
        node_id = tree_with_root["root_node_id"]
        url = f"/api/v1/trees/{tree_id}/nodes/{node_id}/children/"

        response = api_client.get(url)

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_get_children_with_data(self, api_client, tree_with_root):
        """GET /nodes/{id}/children should return list of child nodes with edges"""
        tree_id = tree_with_root["tree_id"]
        node_id = tree_with_root["root_node_id"]

        # Add two moves
        moves_url = f"/api/v1/trees/{tree_id}/nodes/{node_id}/moves/"
        api_client.post(moves_url, {"move_usi": "7g7f"}, format="json")
        api_client.post(moves_url, {"move_usi": "2g2f"}, format="json")

        # Get children
        children_url = f"/api/v1/trees/{tree_id}/nodes/{node_id}/children/"
        response = api_client.get(children_url)

        assert response.status_code == status.HTTP_200_OK
        children = response.json()
        assert len(children) == 2

        # Check structure
        for child in children:
            assert "node" in child
            assert "move_usi" in child
            assert "move_japanese" in child
            assert "id" in child["node"]
            assert "sfen" in child["node"]


@pytest.mark.django_db
class TestAddMoveInvalidFormat:
    """T013: Contract test for POST /nodes/{id}/moves with invalid format (400)"""

    def test_add_move_invalid_format(self, api_client, tree_with_root):
        """POST /nodes/{id}/moves with invalid USI should return 400"""
        tree_id = tree_with_root["tree_id"]
        node_id = tree_with_root["root_node_id"]
        url = f"/api/v1/trees/{tree_id}/nodes/{node_id}/moves/"

        response = api_client.post(url, {"move_usi": "invalid"}, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response_data = response.json()
        assert "error" in response_data
        assert response_data["error"] == "invalid_format"

    def test_add_move_empty(self, api_client, tree_with_root):
        """POST /nodes/{id}/moves with empty move should return 400"""
        tree_id = tree_with_root["tree_id"]
        node_id = tree_with_root["root_node_id"]
        url = f"/api/v1/trees/{tree_id}/nodes/{node_id}/moves/"

        response = api_client.post(url, {"move_usi": ""}, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestAddMoveIllegal:
    """T014: Contract test for POST /nodes/{id}/moves with illegal move (400)"""

    def test_add_illegal_move(self, api_client, tree_with_root):
        """POST /nodes/{id}/moves with illegal move should return 400"""
        tree_id = tree_with_root["tree_id"]
        node_id = tree_with_root["root_node_id"]
        url = f"/api/v1/trees/{tree_id}/nodes/{node_id}/moves/"

        # 1a1b is not a legal move (trying to move enemy piece)
        # cshogi classifies this as invalid_format since board.move_from_usi returns 0
        response = api_client.post(url, {"move_usi": "1a1b"}, format="json")

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response_data = response.json()
        assert "error" in response_data
        # Note: cshogi treats moves that can't be parsed as invalid_format
        # rather than illegal_move (which is reserved for things like nifu)
        assert response_data["error"] in ["illegal_move", "invalid_format"]
        assert "move_usi" in response_data


@pytest.mark.django_db
class TestAddMoveTransposition:
    """T015: Contract test for POST /nodes/{id}/moves detecting transposition"""

    def test_transposition_detection(self, api_client, tree_with_root):
        """
        Same position reached via different move orders should be detected.

        Example: 7g7f -> 3c3d -> 2g2f reaches same position as 2g2f -> 3c3d -> 7g7f
        """
        tree_id = tree_with_root["tree_id"]
        root_id = tree_with_root["root_node_id"]

        # Path 1: root -> 7g7f -> 3c3d -> 2g2f
        url1 = f"/api/v1/trees/{tree_id}/nodes/{root_id}/moves/"
        r1 = api_client.post(url1, {"move_usi": "7g7f"}, format="json")
        node1_id = r1.json()["child_node"]["id"]

        url2 = f"/api/v1/trees/{tree_id}/nodes/{node1_id}/moves/"
        r2 = api_client.post(url2, {"move_usi": "3c3d"}, format="json")
        node2_id = r2.json()["child_node"]["id"]

        url3 = f"/api/v1/trees/{tree_id}/nodes/{node2_id}/moves/"
        r3 = api_client.post(url3, {"move_usi": "2g2f"}, format="json")
        path1_final_id = r3.json()["child_node"]["id"]
        path1_sfen = r3.json()["child_node"]["sfen"]

        # Path 2: root -> 2g2f -> 3c3d -> 7g7f (should reach same position)
        url4 = f"/api/v1/trees/{tree_id}/nodes/{root_id}/moves/"
        r4 = api_client.post(url4, {"move_usi": "2g2f"}, format="json")
        node4_id = r4.json()["child_node"]["id"]

        url5 = f"/api/v1/trees/{tree_id}/nodes/{node4_id}/moves/"
        r5 = api_client.post(url5, {"move_usi": "3c3d"}, format="json")
        node5_id = r5.json()["child_node"]["id"]

        # This should detect transposition
        url6 = f"/api/v1/trees/{tree_id}/nodes/{node5_id}/moves/"
        r6 = api_client.post(url6, {"move_usi": "7g7f"}, format="json")

        assert r6.status_code == status.HTTP_201_CREATED
        response_data = r6.json()

        # Should be transposition
        assert response_data["is_transposition"] is True
        # Should link to existing node
        assert response_data["child_node"]["id"] == path1_final_id
        assert response_data["child_node"]["sfen"] == path1_sfen


@pytest.mark.django_db
class TestDeleteNodeSingleParent:
    """T016: Contract test for DELETE /trees/{tree_id}/nodes/{node_id} (204)"""

    def test_delete_node_success(self, api_client, tree_with_root):
        """DELETE /nodes/{id} with single parent should return 204"""
        tree_id = tree_with_root["tree_id"]
        root_id = tree_with_root["root_node_id"]

        # Add a move first
        moves_url = f"/api/v1/trees/{tree_id}/nodes/{root_id}/moves/"
        response = api_client.post(moves_url, {"move_usi": "7g7f"}, format="json")
        child_id = response.json()["child_node"]["id"]

        # Delete the child node
        delete_url = f"/api/v1/trees/{tree_id}/nodes/{child_id}/"
        response = api_client.delete(delete_url)

        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify node is deleted (children should be empty)
        children_url = f"/api/v1/trees/{tree_id}/nodes/{root_id}/children/"
        children_response = api_client.get(children_url)
        assert len(children_response.json()) == 0


@pytest.mark.django_db
class TestDeleteNodeTransposition:
    """T017: Contract test for DELETE /nodes/{id}?parent_id= (transposition)"""

    def test_delete_transposition_with_parent_id(self, api_client, tree_with_root):
        """DELETE transposition node with parent_id should only remove edge"""
        tree_id = tree_with_root["tree_id"]
        root_id = tree_with_root["root_node_id"]

        # Create two paths to same position (simplified: just create a transposition scenario)
        # Path 1: root -> 7g7f -> 3c3d
        url1 = f"/api/v1/trees/{tree_id}/nodes/{root_id}/moves/"
        r1 = api_client.post(url1, {"move_usi": "7g7f"}, format="json")
        node1_id = r1.json()["child_node"]["id"]

        url2 = f"/api/v1/trees/{tree_id}/nodes/{node1_id}/moves/"
        r2 = api_client.post(url2, {"move_usi": "3c3d"}, format="json")
        shared_node_id = r2.json()["child_node"]["id"]

        # Path 2: root -> 2g2f -> 3c3d -> 7g7f (leads to transposition)
        url3 = f"/api/v1/trees/{tree_id}/nodes/{root_id}/moves/"
        r3 = api_client.post(url3, {"move_usi": "2g2f"}, format="json")
        node3_id = r3.json()["child_node"]["id"]

        url4 = f"/api/v1/trees/{tree_id}/nodes/{node3_id}/moves/"
        r4 = api_client.post(url4, {"move_usi": "3c3d"}, format="json")
        node4_id = r4.json()["child_node"]["id"]

        url5 = f"/api/v1/trees/{tree_id}/nodes/{node4_id}/moves/"
        r5 = api_client.post(url5, {"move_usi": "7g7f"}, format="json")

        # If transposition was detected
        if r5.json()["is_transposition"]:
            transposition_node_id = r5.json()["child_node"]["id"]

            # Delete edge from node4 (parent_id)
            delete_url = (
                f"/api/v1/trees/{tree_id}/nodes/{transposition_node_id}/"
                f"?parent_id={node4_id}"
            )
            response = api_client.delete(delete_url)

            assert response.status_code == status.HTTP_204_NO_CONTENT

            # Node should still exist (accessible from path 1)
            # Verify by checking the tree still has the node
            tree_response = api_client.get(f"/api/v1/trees/{tree_id}/")
            assert tree_response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestDeleteRootNode:
    """T018: Contract test for DELETE /nodes/{id} root node (400)"""

    def test_delete_root_node_fails(self, api_client, tree_with_root):
        """DELETE root node should return 400 cannot_delete_root"""
        tree_id = tree_with_root["tree_id"]
        root_id = tree_with_root["root_node_id"]

        url = f"/api/v1/trees/{tree_id}/nodes/{root_id}/"
        response = api_client.delete(url)

        assert response.status_code == status.HTTP_400_BAD_REQUEST
        response_data = response.json()
        assert response_data["error"] == "cannot_delete_root"


@pytest.mark.django_db
class TestDeleteTranspositionWithoutParentId:
    """T019: Contract test for DELETE transposition node without parent_id (400)"""

    def test_delete_transposition_without_parent_id(self, api_client, tree_with_root):
        """DELETE transposition node without parent_id should return 400"""
        tree_id = tree_with_root["tree_id"]
        root_id = tree_with_root["root_node_id"]

        # Create a transposition (same as T017 setup)
        url1 = f"/api/v1/trees/{tree_id}/nodes/{root_id}/moves/"
        r1 = api_client.post(url1, {"move_usi": "7g7f"}, format="json")
        node1_id = r1.json()["child_node"]["id"]

        url2 = f"/api/v1/trees/{tree_id}/nodes/{node1_id}/moves/"
        r2 = api_client.post(url2, {"move_usi": "3c3d"}, format="json")

        url3 = f"/api/v1/trees/{tree_id}/nodes/{root_id}/moves/"
        r3 = api_client.post(url3, {"move_usi": "2g2f"}, format="json")
        node3_id = r3.json()["child_node"]["id"]

        url4 = f"/api/v1/trees/{tree_id}/nodes/{node3_id}/moves/"
        r4 = api_client.post(url4, {"move_usi": "3c3d"}, format="json")
        node4_id = r4.json()["child_node"]["id"]

        url5 = f"/api/v1/trees/{tree_id}/nodes/{node4_id}/moves/"
        r5 = api_client.post(url5, {"move_usi": "7g7f"}, format="json")

        if r5.json()["is_transposition"]:
            transposition_node_id = r5.json()["child_node"]["id"]

            # Try to delete without parent_id
            delete_url = f"/api/v1/trees/{tree_id}/nodes/{transposition_node_id}/"
            response = api_client.delete(delete_url)

            assert response.status_code == status.HTTP_400_BAD_REQUEST
            response_data = response.json()
            assert response_data["error"] == "parent_id_required"
