"""
NodeService - ノード操作を担当

Phase 3 の Service 層実装
"""

from typing import TYPE_CHECKING

from django.db import transaction

from core.shogi.exceptions import IllegalMoveError, InvalidMoveError
from core.shogi.rules import apply_move, validate_move
from trees.models import Edge, Node

if TYPE_CHECKING:
    import uuid


class DuplicateMoveError(Exception):
    """同じ指し手が既に存在する場合のエラー"""

    def __init__(self, message: str, move_usi: str | None = None):
        super().__init__(message)
        self.move_usi = move_usi


class NodeService:
    """ノード操作を担当"""

    @transaction.atomic
    def add_move(
        self, node: Node, move_usi: str
    ) -> tuple[Node, Edge, bool]:
        """
        指し手を追加し、子ノードを作成または転置を検出する。

        Args:
            node: 親ノード
            move_usi: USI形式の指し手

        Returns:
            tuple: (child_node, edge, is_transposition)

        Raises:
            InvalidMoveError: 指し手の形式が不正
            IllegalMoveError: 合法でない指し手
            DuplicateMoveError: 同じ指し手が既に存在
        """
        # 既存の同じ指し手チェック
        if Edge.objects.filter(parent=node, move_usi=move_usi).exists():
            raise DuplicateMoveError(
                f"指し手 {move_usi} は既に存在します",
                move_usi=move_usi,
            )

        # 合法手検証（InvalidMoveError, IllegalMoveError を raise）
        validate_move(node.sfen, move_usi)

        # 新しい局面を計算
        new_sfen = apply_move(node.sfen, move_usi)

        # 転置検出: 同一ツリー内で同じ SFEN のノードを検索
        existing_node = Node.objects.filter(
            tree=node.tree,
            sfen=new_sfen,
        ).first()

        if existing_node:
            # 転置: 既存ノードへエッジを作成
            edge = Edge.objects.create(
                parent=node,
                child=existing_node,
                move_usi=move_usi,
            )
            return existing_node, edge, True
        else:
            # 新規ノード作成
            new_node = Node.objects.create(
                tree=node.tree,
                sfen=new_sfen,
                ply=node.ply + 1,
            )
            edge = Edge.objects.create(
                parent=node,
                child=new_node,
                move_usi=move_usi,
            )
            return new_node, edge, False

    def get_children(self, node: Node) -> list[dict]:
        """
        子ノード一覧を取得

        Returns:
            list: [{"node": Node, "move_usi": str, "move_japanese": str}, ...]
        """
        edges = node.child_edges.select_related("child").all()
        return [
            {
                "node": edge.child,
                "move_usi": edge.move_usi,
                "move_japanese": edge.move_japanese,
            }
            for edge in edges
        ]

    @transaction.atomic
    def delete_node(
        self, node: Node, parent_id: "uuid.UUID | None" = None
    ) -> None:
        """
        ノードを削除する。

        Args:
            node: 削除対象ノード
            parent_id: 転置ノードの場合、削除するエッジの親ノードID

        Raises:
            ValueError: ルートノードの削除、または転置ノードで parent_id 未指定
        """
        if node.is_root:
            raise ValueError("ルートノードは削除できません")

        parent_edges = node.parent_edges.all()
        parent_count = parent_edges.count()

        if parent_count > 1:
            # 転置ノード: parent_id 必須
            if parent_id is None:
                raise ValueError("転置ノードの削除には parent_id が必要です")

            edge = parent_edges.filter(parent_id=parent_id).first()
            if edge is None:
                raise ValueError("指定された親からのエッジが見つかりません")

            # エッジのみ削除（ノードは残る）
            edge.delete()
        else:
            # 単一親ノード: ノードと子孫を削除
            self._delete_subtree(node)

    def _delete_subtree(self, node: Node) -> None:
        """サブツリーを再帰的に削除"""
        # 子ノードを取得し、各子について親エッジが1つだけなら再帰削除
        for edge in node.child_edges.all():
            child = edge.child
            # 子ノードの親エッジがこの1つだけなら子も削除
            if child.parent_edges.count() == 1:
                self._delete_subtree(child)

        # このノードを削除（関連するエッジも CASCADE で削除）
        node.delete()
