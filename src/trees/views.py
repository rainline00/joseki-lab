"""
ViewSets for Trees app.

定跡ツリーとノードの REST API ViewSet を定義
"""

from uuid import UUID

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.request import Request
from rest_framework.response import Response

from core.shogi.exceptions import IllegalMoveError, InvalidMoveError
from trees.models import JosekiTree, Node
from trees.serializers import (
    ChildNodeSerializer,
    EdgeSerializer,
    JosekiTreeCreateSerializer,
    JosekiTreeSerializer,
    JosekiTreeSummarySerializer,
    JosekiTreeUpdateSerializer,
    MoveCreateSerializer,
    MoveResultSerializer,
    NodeSerializer,
)
from trees.services import DuplicateMoveError, NodeService, TreeService


class JosekiTreeViewSet(viewsets.ViewSet):
    """
    定跡ツリーの CRUD API

    - POST /trees/ - ツリー作成
    - GET /trees/ - ツリー一覧
    - GET /trees/{id}/ - ツリー詳細
    - PATCH /trees/{id}/ - ツリー更新
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tree_service = TreeService()

    def create(self, request: Request) -> Response:
        """POST /trees/ - ツリー作成"""
        serializer = JosekiTreeCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        tree = self.tree_service.create_tree(
            name=serializer.validated_data["name"],
            description=serializer.validated_data.get("description", ""),
        )

        output_serializer = JosekiTreeSerializer(tree)
        return Response(
            output_serializer.data,
            status=status.HTTP_201_CREATED,
        )

    def list(self, request: Request) -> Response:
        """GET /trees/ - ツリー一覧"""
        trees = self.tree_service.list_trees()
        serializer = JosekiTreeSummarySerializer(trees, many=True)
        return Response(serializer.data)

    def retrieve(self, request: Request, pk: str = None) -> Response:
        """GET /trees/{id}/ - ツリー詳細"""
        try:
            tree_id = UUID(pk)
        except ValueError:
            return Response(
                {"error": "not_found", "message": "無効なツリーIDです"},
                status=status.HTTP_404_NOT_FOUND,
            )

        tree = self.tree_service.get_tree(tree_id)
        if tree is None:
            return Response(
                {"error": "not_found", "message": "ツリーが見つかりません"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = JosekiTreeSerializer(tree)
        return Response(serializer.data)

    def partial_update(self, request: Request, pk: str = None) -> Response:
        """PATCH /trees/{id}/ - ツリー更新"""
        try:
            tree_id = UUID(pk)
        except ValueError:
            return Response(
                {"error": "not_found", "message": "無効なツリーIDです"},
                status=status.HTTP_404_NOT_FOUND,
            )

        tree = self.tree_service.get_tree(tree_id)
        if tree is None:
            return Response(
                {"error": "not_found", "message": "ツリーが見つかりません"},
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = JosekiTreeUpdateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST,
            )

        tree = self.tree_service.update_tree(
            tree=tree,
            name=serializer.validated_data.get("name"),
            description=serializer.validated_data.get("description"),
        )

        output_serializer = JosekiTreeSerializer(tree)
        return Response(output_serializer.data)


class NodeViewSet(viewsets.ViewSet):
    """
    ノード操作の API

    - POST /trees/{tree_id}/nodes/{node_id}/moves/ - 指し手追加
    - GET /trees/{tree_id}/nodes/{node_id}/children/ - 子ノード一覧
    - DELETE /trees/{tree_id}/nodes/{node_id}/ - ノード削除
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.node_service = NodeService()
        self.tree_service = TreeService()

    def _get_node(
        self, tree_id: str, node_id: str
    ) -> tuple[Node | None, Response | None]:
        """
        ツリーIDとノードIDからノードを取得

        Returns:
            tuple: (node, error_response)
            ノードが見つかった場合は (node, None)
            エラーの場合は (None, error_response)
        """
        try:
            tree_uuid = UUID(tree_id)
            node_uuid = UUID(node_id)
        except ValueError:
            return None, Response(
                {"error": "not_found", "message": "無効なIDです"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # ツリーの存在確認
        tree = self.tree_service.get_tree(tree_uuid)
        if tree is None:
            return None, Response(
                {"error": "not_found", "message": "ツリーが見つかりません"},
                status=status.HTTP_404_NOT_FOUND,
            )

        # ノードの取得
        try:
            node = Node.objects.get(id=node_uuid, tree=tree)
        except Node.DoesNotExist:
            return None, Response(
                {"error": "not_found", "message": "ノードが見つかりません"},
                status=status.HTTP_404_NOT_FOUND,
            )

        return node, None

    @action(detail=True, methods=["post"], url_path="moves")
    def add_move(
        self, request: Request, tree_id: str = None, node_id: str = None
    ) -> Response:
        """POST /trees/{tree_id}/nodes/{node_id}/moves/ - 指し手追加"""
        node, error = self._get_node(tree_id, node_id)
        if error:
            return error

        serializer = MoveCreateSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {
                    "error": "invalid_format",
                    "message": "指し手の形式が不正です",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        move_usi = serializer.validated_data["move_usi"]

        try:
            child_node, edge, is_transposition = self.node_service.add_move(
                node=node,
                move_usi=move_usi,
            )
        except InvalidMoveError:
            return Response(
                {
                    "error": "invalid_format",
                    "message": f"無効な指し手形式です: {move_usi}",
                    "move_usi": move_usi,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except IllegalMoveError:
            return Response(
                {
                    "error": "illegal_move",
                    "message": f"合法でない指し手です: {move_usi}",
                    "move_usi": move_usi,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        except DuplicateMoveError as e:
            return Response(
                {
                    "error": "duplicate_move",
                    "message": str(e),
                },
                status=status.HTTP_409_CONFLICT,
            )

        result = MoveResultSerializer(
            {
                "edge": edge,
                "child_node": child_node,
                "is_transposition": is_transposition,
            }
        )
        return Response(result.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=["get"], url_path="children")
    def children(
        self, request: Request, tree_id: str = None, node_id: str = None
    ) -> Response:
        """GET /trees/{tree_id}/nodes/{node_id}/children/ - 子ノード一覧"""
        node, error = self._get_node(tree_id, node_id)
        if error:
            return error

        children = self.node_service.get_children(node)
        result = [
            {
                "node": NodeSerializer(child["node"]).data,
                "move_usi": child["move_usi"],
                "move_japanese": child["move_japanese"],
            }
            for child in children
        ]
        return Response(result)

    def destroy(
        self, request: Request, tree_id: str = None, node_id: str = None
    ) -> Response:
        """DELETE /trees/{tree_id}/nodes/{node_id}/ - ノード削除"""
        node, error = self._get_node(tree_id, node_id)
        if error:
            return error

        # parent_id クエリパラメータの取得
        parent_id_str = request.query_params.get("parent_id")
        parent_id = None
        if parent_id_str:
            try:
                parent_id = UUID(parent_id_str)
            except ValueError:
                return Response(
                    {
                        "error": "invalid_format",
                        "message": "無効な parent_id です",
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        try:
            self.node_service.delete_node(node, parent_id=parent_id)
        except ValueError as e:
            error_message = str(e)
            if "ルートノード" in error_message:
                return Response(
                    {
                        "error": "cannot_delete_root",
                        "message": error_message,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            elif "parent_id" in error_message:
                return Response(
                    {
                        "error": "parent_id_required",
                        "message": error_message,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            else:
                return Response(
                    {
                        "error": "bad_request",
                        "message": error_message,
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        return Response(status=status.HTTP_204_NO_CONTENT)
