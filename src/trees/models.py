"""
Trees app models.

定跡ツリー、ノード、エッジのモデル定義
"""

import uuid

from django.db import models
from django.utils import timezone


class JosekiTree(models.Model):
    """定跡ツリー

    定跡の集合を管理するルートエンティティ
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200, verbose_name="ツリー名")
    description = models.TextField(blank=True, verbose_name="説明")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")
    is_deleted = models.BooleanField(default=False, db_index=True, verbose_name="削除フラグ")
    deleted_at = models.DateTimeField(
        null=True, blank=True, db_index=True, verbose_name="削除日時"
    )

    class Meta:
        db_table = "joseki_trees"
        ordering = ["-updated_at"]
        verbose_name = "定跡ツリー"
        verbose_name_plural = "定跡ツリー"

    def __str__(self) -> str:
        return self.name

    def soft_delete(self) -> None:
        """ソフトデリート（is_deleted=True, deleted_at=now）"""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=["is_deleted", "deleted_at"])

    def restore(self) -> None:
        """ソフトデリートを解除"""
        self.is_deleted = False
        self.deleted_at = None
        self.save(update_fields=["is_deleted", "deleted_at"])

    @property
    def root_node(self) -> "Node | None":
        """ルートノード（初期局面のノード）を返す"""
        return self.nodes.filter(parent_edges__isnull=True).first()


class Node(models.Model):
    """ノード（局面）

    定跡ツリー内の1つの局面を表す
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tree = models.ForeignKey(
        JosekiTree,
        on_delete=models.CASCADE,
        related_name="nodes",
        verbose_name="所属ツリー",
    )
    sfen = models.CharField(
        max_length=200, db_index=True, verbose_name="SFEN（手数なし）"
    )
    ply = models.IntegerField(default=0, verbose_name="手数")
    comment = models.TextField(blank=True, verbose_name="コメント")
    evaluation = models.IntegerField(
        null=True, blank=True, verbose_name="評価値（centipawn）"
    )
    metadata = models.JSONField(default=dict, blank=True, verbose_name="メタデータ")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新日時")

    class Meta:
        db_table = "nodes"
        constraints = [
            models.UniqueConstraint(
                fields=["tree", "sfen"], name="unique_node_per_tree_position"
            )
        ]
        verbose_name = "ノード"
        verbose_name_plural = "ノード"

    def __str__(self) -> str:
        return f"{self.tree.name}: {self.sfen[:30]}..."

    @property
    def is_root(self) -> bool:
        """ルートノードかどうか"""
        return not self.parent_edges.exists()

    @property
    def sfen_with_ply(self) -> str:
        """手数を含む SFEN を返す（CD-004）"""
        return f"{self.sfen} {self.ply}"

    def get_children(self):
        """子ノードへのエッジを取得"""
        return self.child_edges.all()

    def get_parents(self):
        """親ノードからのエッジを取得（転置対応）"""
        return self.parent_edges.all()


class Edge(models.Model):
    """エッジ（指し手）

    ノード間の遷移（指し手）を表す
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    parent = models.ForeignKey(
        Node,
        on_delete=models.CASCADE,
        related_name="child_edges",
        verbose_name="親ノード",
    )
    child = models.ForeignKey(
        Node,
        on_delete=models.CASCADE,
        related_name="parent_edges",
        verbose_name="子ノード",
    )
    move_usi = models.CharField(max_length=10, verbose_name="USI形式の指し手")
    move_japanese = models.CharField(
        max_length=20, blank=True, verbose_name="日本語表記の指し手"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")

    class Meta:
        db_table = "edges"
        constraints = [
            models.UniqueConstraint(
                fields=["parent", "move_usi"], name="unique_move_from_parent"
            ),
            models.CheckConstraint(
                condition=~models.Q(parent=models.F("child")), name="no_self_reference"
            ),
        ]
        verbose_name = "エッジ"
        verbose_name_plural = "エッジ"

    def __str__(self) -> str:
        return f"{self.move_usi} ({self.move_japanese})"
