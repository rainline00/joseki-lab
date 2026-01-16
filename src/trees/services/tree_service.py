"""
TreeService - 定跡ツリーの作成・管理を担当

Phase 3 の Service 層実装
"""

from typing import TYPE_CHECKING

from core.shogi.position import get_initial_sfen
from trees.models import JosekiTree, Node

if TYPE_CHECKING:
    import uuid


class TreeService:
    """定跡ツリーの作成・管理を担当"""

    def create_tree(self, name: str, description: str = "") -> JosekiTree:
        """
        定跡ツリーを作成し、ルートノード（初期局面）を自動作成する。

        Args:
            name: ツリー名
            description: 説明（オプション）

        Returns:
            JosekiTree: 作成されたツリー
        """
        tree = JosekiTree.objects.create(name=name, description=description)

        # ルートノード（平手初期局面）を自動作成
        Node.objects.create(
            tree=tree,
            sfen=get_initial_sfen(),
            ply=0,
        )

        return tree

    def get_tree(self, tree_id: "uuid.UUID") -> JosekiTree | None:
        """ツリーを取得（削除済み除外）"""
        return JosekiTree.objects.filter(
            id=tree_id,
            is_deleted=False,
        ).first()

    def list_trees(self, include_deleted: bool = False) -> list[JosekiTree]:
        """ツリー一覧を取得"""
        qs = JosekiTree.objects.all()
        if not include_deleted:
            qs = qs.filter(is_deleted=False)
        return list(qs)

    def update_tree(
        self,
        tree: JosekiTree,
        name: str | None = None,
        description: str | None = None,
    ) -> JosekiTree:
        """ツリーを更新"""
        if name is not None:
            tree.name = name
        if description is not None:
            tree.description = description
        tree.save()
        return tree
