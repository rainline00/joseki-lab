"""
Integration tests for tree workflow.

Tests complete user workflows for tree creation, move addition, etc.
Phase 3.2: TDD Red phase - tests should fail until implementation.
"""

import pytest
from rest_framework import status
from rest_framework.test import APIClient

# 平手初期局面の SFEN
INITIAL_SFEN = "lnsgkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL b -"


@pytest.fixture
def api_client():
    """DRF APIClient fixture"""
    return APIClient()


@pytest.mark.django_db
class TestTreeCreationWorkflow:
    """T020: Integration test for tree creation with auto root node"""

    def test_create_tree_workflow(self, api_client):
        """
        Complete workflow:
        1. Create a tree
        2. Verify root node is automatically created
        3. Root node has correct initial SFEN
        """
        # Step 1: Create tree
        create_url = "/api/v1/trees/"
        response = api_client.post(
            create_url,
            {"name": "矢倉定跡", "description": "矢倉戦法の基本定跡"},
            format="json",
        )

        assert response.status_code == status.HTTP_201_CREATED
        tree = response.json()
        tree_id = tree["id"]

        # Step 2: Verify root node exists
        assert tree["root_node"] is not None
        root_node = tree["root_node"]
        assert root_node["is_root"] is True

        # Step 3: Root node has initial SFEN
        assert root_node["sfen"] == INITIAL_SFEN
        assert root_node["ply"] == 0

        # Step 4: Verify via GET
        get_url = f"/api/v1/trees/{tree_id}/"
        get_response = api_client.get(get_url)
        assert get_response.status_code == status.HTTP_200_OK
        assert get_response.json()["root_node"]["sfen"] == INITIAL_SFEN


@pytest.mark.django_db
class TestTreeCRUDWorkflow:
    """T021: Integration test for tree CRUD operations"""

    def test_tree_crud_workflow(self, api_client):
        """
        Complete CRUD workflow:
        1. Create tree
        2. Read tree (list and detail)
        3. Update tree
        4. Verify changes
        """
        base_url = "/api/v1/trees/"

        # Create
        create_response = api_client.post(
            base_url,
            {"name": "初期名", "description": "初期説明"},
            format="json",
        )
        assert create_response.status_code == status.HTTP_201_CREATED
        tree_id = create_response.json()["id"]

        # Read (list)
        list_response = api_client.get(base_url)
        assert list_response.status_code == status.HTTP_200_OK
        trees = list_response.json()
        assert len(trees) == 1
        assert trees[0]["name"] == "初期名"

        # Read (detail)
        detail_url = f"{base_url}{tree_id}/"
        detail_response = api_client.get(detail_url)
        assert detail_response.status_code == status.HTTP_200_OK
        assert detail_response.json()["name"] == "初期名"

        # Update
        update_response = api_client.patch(
            detail_url,
            {"name": "更新名", "description": "更新説明"},
            format="json",
        )
        assert update_response.status_code == status.HTTP_200_OK
        assert update_response.json()["name"] == "更新名"
        assert update_response.json()["description"] == "更新説明"

        # Verify update persisted
        verify_response = api_client.get(detail_url)
        assert verify_response.json()["name"] == "更新名"


@pytest.mark.django_db
class TestAddMovesWorkflow:
    """T022: Integration test for adding moves and creating branches"""

    def test_add_moves_and_branches(self, api_client):
        """
        Complete workflow:
        1. Create tree
        2. Add first move (7g7f)
        3. Add branch (2g2f) from root
        4. Add continuation from 7g7f
        5. Verify tree structure
        """
        # Create tree
        tree_response = api_client.post(
            "/api/v1/trees/",
            {"name": "分岐テスト"},
            format="json",
        )
        tree = tree_response.json()
        tree_id = tree["id"]
        root_id = tree["root_node"]["id"]

        # Add first move: 7g7f (76歩)
        move1_url = f"/api/v1/trees/{tree_id}/nodes/{root_id}/moves/"
        move1_response = api_client.post(
            move1_url, {"move_usi": "7g7f"}, format="json"
        )
        assert move1_response.status_code == status.HTTP_201_CREATED
        node1_id = move1_response.json()["child_node"]["id"]
        assert move1_response.json()["child_node"]["ply"] == 1

        # Add branch: 2g2f (26歩) from root
        move2_response = api_client.post(
            move1_url, {"move_usi": "2g2f"}, format="json"
        )
        assert move2_response.status_code == status.HTTP_201_CREATED
        node2_id = move2_response.json()["child_node"]["id"]
        assert move2_response.json()["child_node"]["ply"] == 1

        # Verify root has 2 children
        children_url = f"/api/v1/trees/{tree_id}/nodes/{root_id}/children/"
        children_response = api_client.get(children_url)
        assert len(children_response.json()) == 2

        # Add continuation from 7g7f: 3c3d
        move3_url = f"/api/v1/trees/{tree_id}/nodes/{node1_id}/moves/"
        move3_response = api_client.post(
            move3_url, {"move_usi": "3c3d"}, format="json"
        )
        assert move3_response.status_code == status.HTTP_201_CREATED
        assert move3_response.json()["child_node"]["ply"] == 2

        # Verify tree structure
        tree_detail = api_client.get(f"/api/v1/trees/{tree_id}/").json()
        assert tree_detail["node_count"] == 4  # root + 2 branches + 1 continuation


@pytest.mark.django_db
class TestIllegalMoveRejection:
    """T023: Integration test for illegal move rejection"""

    def test_reject_illegal_moves(self, api_client):
        """
        Test various illegal moves are rejected:
        1. Invalid piece move (e.g., move from empty square)
        2. Nifu (double pawn) - harder to test without specific setup
        3. Invalid USI format
        """
        # Create tree
        tree_response = api_client.post(
            "/api/v1/trees/",
            {"name": "反則テスト"},
            format="json",
        )
        tree = tree_response.json()
        tree_id = tree["id"]
        root_id = tree["root_node"]["id"]

        moves_url = f"/api/v1/trees/{tree_id}/nodes/{root_id}/moves/"

        # Test 1: Invalid move (moving from wrong position)
        response1 = api_client.post(
            moves_url, {"move_usi": "5e5f"}, format="json"
        )
        assert response1.status_code == status.HTTP_400_BAD_REQUEST
        assert response1.json()["error"] in ["illegal_move", "invalid_format"]

        # Test 2: Invalid format
        response2 = api_client.post(
            moves_url, {"move_usi": "abc"}, format="json"
        )
        assert response2.status_code == status.HTTP_400_BAD_REQUEST
        assert response2.json()["error"] == "invalid_format"

        # Test 3: Valid move should work
        response3 = api_client.post(
            moves_url, {"move_usi": "7g7f"}, format="json"
        )
        assert response3.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
class TestTranspositionDetection:
    """T024: Integration test for transposition detection and merging"""

    def test_transposition_merge(self, api_client):
        """
        Test that same position via different paths is detected:
        Path 1: 7g7f -> 3c3d -> 2g2f
        Path 2: 2g2f -> 3c3d -> 7g7f
        Both should reach the same position (transposition)
        """
        # Create tree
        tree_response = api_client.post(
            "/api/v1/trees/",
            {"name": "転置テスト"},
            format="json",
        )
        tree = tree_response.json()
        tree_id = tree["id"]
        root_id = tree["root_node"]["id"]

        # Path 1: root -> 7g7f -> 3c3d -> 2g2f
        path1_moves = ["7g7f", "3c3d", "2g2f"]
        current_node = root_id
        for move in path1_moves:
            url = f"/api/v1/trees/{tree_id}/nodes/{current_node}/moves/"
            response = api_client.post(url, {"move_usi": move}, format="json")
            assert response.status_code == status.HTTP_201_CREATED
            current_node = response.json()["child_node"]["id"]

        path1_final_node = current_node
        path1_final_sfen = api_client.get(
            f"/api/v1/trees/{tree_id}/"
        ).json()  # Just verify tree exists

        # Path 2: root -> 2g2f -> 3c3d -> 7g7f
        path2_moves = ["2g2f", "3c3d", "7g7f"]
        current_node = root_id
        for i, move in enumerate(path2_moves):
            url = f"/api/v1/trees/{tree_id}/nodes/{current_node}/moves/"
            response = api_client.post(url, {"move_usi": move}, format="json")
            assert response.status_code == status.HTTP_201_CREATED

            if i == len(path2_moves) - 1:
                # Last move should detect transposition
                assert response.json()["is_transposition"] is True
                assert response.json()["child_node"]["id"] == path1_final_node
            else:
                current_node = response.json()["child_node"]["id"]


@pytest.mark.django_db
class TestNodeDeletionSingleParent:
    """T025: Integration test for node deletion with single parent (cascading)"""

    def test_delete_node_with_children(self, api_client):
        """
        Delete a node that has children should cascade:
        root -> A -> B -> C
        Deleting A should also delete B and C
        """
        # Create tree
        tree_response = api_client.post(
            "/api/v1/trees/",
            {"name": "削除テスト"},
            format="json",
        )
        tree = tree_response.json()
        tree_id = tree["id"]
        root_id = tree["root_node"]["id"]

        # Build path: root -> A (7g7f) -> B (3c3d) -> C (2g2f)
        moves_url = f"/api/v1/trees/{tree_id}/nodes/{root_id}/moves/"
        r1 = api_client.post(moves_url, {"move_usi": "7g7f"}, format="json")
        node_a_id = r1.json()["child_node"]["id"]

        url2 = f"/api/v1/trees/{tree_id}/nodes/{node_a_id}/moves/"
        r2 = api_client.post(url2, {"move_usi": "3c3d"}, format="json")
        node_b_id = r2.json()["child_node"]["id"]

        url3 = f"/api/v1/trees/{tree_id}/nodes/{node_b_id}/moves/"
        api_client.post(url3, {"move_usi": "2g2f"}, format="json")

        # Verify tree has 4 nodes
        tree_detail = api_client.get(f"/api/v1/trees/{tree_id}/").json()
        assert tree_detail["node_count"] == 4

        # Delete node A
        delete_url = f"/api/v1/trees/{tree_id}/nodes/{node_a_id}/"
        delete_response = api_client.delete(delete_url)
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT

        # Verify tree now has only root node
        tree_detail_after = api_client.get(f"/api/v1/trees/{tree_id}/").json()
        assert tree_detail_after["node_count"] == 1


@pytest.mark.django_db
class TestTranspositionEdgeDeletion:
    """T026: Integration test for transposition node edge deletion"""

    def test_delete_edge_preserves_node(self, api_client):
        """
        When deleting an edge to a transposition node:
        - The edge should be removed
        - The node should remain (accessible via other path)
        """
        # Create tree
        tree_response = api_client.post(
            "/api/v1/trees/",
            {"name": "転置削除テスト"},
            format="json",
        )
        tree = tree_response.json()
        tree_id = tree["id"]
        root_id = tree["root_node"]["id"]

        # Build two paths to same position
        # Path 1: root -> 7g7f -> 3c3d
        url1 = f"/api/v1/trees/{tree_id}/nodes/{root_id}/moves/"
        r1 = api_client.post(url1, {"move_usi": "7g7f"}, format="json")
        node1_id = r1.json()["child_node"]["id"]

        url2 = f"/api/v1/trees/{tree_id}/nodes/{node1_id}/moves/"
        r2 = api_client.post(url2, {"move_usi": "3c3d"}, format="json")
        shared_node_id = r2.json()["child_node"]["id"]
        shared_sfen = r2.json()["child_node"]["sfen"]

        # Path 2: root -> 2g2f -> 3c3d -> 7g7f (should be transposition at end)
        r3 = api_client.post(url1, {"move_usi": "2g2f"}, format="json")
        node3_id = r3.json()["child_node"]["id"]

        url4 = f"/api/v1/trees/{tree_id}/nodes/{node3_id}/moves/"
        r4 = api_client.post(url4, {"move_usi": "3c3d"}, format="json")
        node4_id = r4.json()["child_node"]["id"]

        url5 = f"/api/v1/trees/{tree_id}/nodes/{node4_id}/moves/"
        r5 = api_client.post(url5, {"move_usi": "7g7f"}, format="json")

        if r5.json()["is_transposition"]:
            transposition_node_id = r5.json()["child_node"]["id"]

            # Delete edge from path 2
            delete_url = (
                f"/api/v1/trees/{tree_id}/nodes/{transposition_node_id}/"
                f"?parent_id={node4_id}"
            )
            delete_response = api_client.delete(delete_url)
            assert delete_response.status_code == status.HTTP_204_NO_CONTENT

            # Node should still exist via path 1
            # Check by verifying children of node1
            children_url = f"/api/v1/trees/{tree_id}/nodes/{node1_id}/children/"
            children_response = api_client.get(children_url)
            children = children_response.json()

            # Should still have the child with matching SFEN
            assert any(c["node"]["sfen"] == shared_sfen for c in children)
