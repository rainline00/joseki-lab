# Data Model: Phase 3 - 定跡ツリーの作成と手順入力 (MVP)

**Feature**: 005-joseki-manager-phase3
**Date**: 2026-01-16
**Status**: Draft
**Base**: [004-joseki-manager-phase2/data-model.md](../004-joseki-manager-phase2/data-model.md)

## 概要

Phase 3 では新しいエンティティの追加は行わない。Phase 2 で実装済みのモデル（JosekiTree, Node, Edge）をそのまま使用する。

このドキュメントでは、Phase 3 で追加する **Service 層** と **Serializer** の設計を定義する。

---

## 使用する既存モデル

Phase 2 で実装済み（変更なし）:

- **JosekiTree**: 定跡ツリーのルートエンティティ
- **Node**: 局面を表すノード（SFEN + ply）
- **Edge**: ノード間の指し手（move_usi, move_japanese）

詳細は [004-joseki-manager-phase2/data-model.md](../004-joseki-manager-phase2/data-model.md) を参照。

---

## Service Layer 設計

### TreeService

**ファイル**: `src/trees/services/tree_service.py`

```python
from typing import TYPE_CHECKING

from src.core.shogi.position import get_initial_sfen
from src.trees.models import JosekiTree, Node

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
            is_deleted=False
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
        description: str | None = None
    ) -> JosekiTree:
        """ツリーを更新"""
        if name is not None:
            tree.name = name
        if description is not None:
            tree.description = description
        tree.save()
        return tree
```

---

### NodeService

**ファイル**: `src/trees/services/node_service.py`

```python
from typing import TYPE_CHECKING

from django.db import transaction

from src.core.shogi.exceptions import IllegalMoveError, InvalidMoveError
from src.core.shogi.rules import apply_move, validate_move
from src.trees.models import Edge, Node

if TYPE_CHECKING:
    import uuid


class DuplicateMoveError(Exception):
    """同じ指し手が既に存在する場合のエラー"""
    pass


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
            raise DuplicateMoveError(f"指し手 {move_usi} は既に存在します")

        # 合法手検証（InvalidMoveError, IllegalMoveError を raise）
        validate_move(node.sfen, move_usi)

        # 新しい局面を計算
        new_sfen = apply_move(node.sfen, move_usi)

        # 転置検出: 同一ツリー内で同じ SFEN のノードを検索
        existing_node = Node.objects.filter(
            tree=node.tree,
            sfen=new_sfen
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
            # Edge の CASCADE で子へのエッジも削除される
            # 子ノードの削除は再帰的に行う必要がある
            self._delete_subtree(node)

    def _delete_subtree(self, node: Node) -> None:
        """サブツリーを再帰的に削除"""
        # 子ノードを取得
        for edge in node.child_edges.all():
            child = edge.child
            # 子ノードの親エッジがこの1つだけなら子も削除
            if child.parent_edges.count() == 1:
                self._delete_subtree(child)

        # このノードを削除（関連するエッジも CASCADE で削除）
        node.delete()
```

---

## Serializer 設計

**ファイル**: `src/trees/serializers.py`

### JosekiTree 関連

```python
from rest_framework import serializers
from src.trees.models import JosekiTree, Node, Edge


class JosekiTreeCreateSerializer(serializers.Serializer):
    """POST /trees 入力"""
    name = serializers.CharField(max_length=200, min_length=1)
    description = serializers.CharField(required=False, allow_blank=True, default="")


class JosekiTreeUpdateSerializer(serializers.Serializer):
    """PATCH /trees/{id} 入力"""
    name = serializers.CharField(max_length=200, min_length=1, required=False)
    description = serializers.CharField(required=False, allow_blank=True)


class NodeSerializer(serializers.ModelSerializer):
    """ノード出力（基本）"""
    is_root = serializers.BooleanField(read_only=True)

    class Meta:
        model = Node
        fields = [
            "id", "tree_id", "sfen", "ply", "comment", "evaluation",
            "metadata", "is_root", "created_at", "updated_at"
        ]


class JosekiTreeSummarySerializer(serializers.ModelSerializer):
    """GET /trees 一覧出力"""
    node_count = serializers.SerializerMethodField()

    class Meta:
        model = JosekiTree
        fields = [
            "id", "name", "description", "node_count",
            "created_at", "updated_at", "is_deleted", "deleted_at"
        ]

    def get_node_count(self, obj):
        return obj.nodes.count()


class JosekiTreeSerializer(serializers.ModelSerializer):
    """GET /trees/{id} 出力"""
    root_node = serializers.SerializerMethodField()
    node_count = serializers.SerializerMethodField()

    class Meta:
        model = JosekiTree
        fields = [
            "id", "name", "description", "node_count",
            "created_at", "updated_at", "is_deleted", "deleted_at",
            "root_node"
        ]

    def get_root_node(self, obj):
        root = obj.root_node
        if root:
            return NodeSerializer(root).data
        return None

    def get_node_count(self, obj):
        return obj.nodes.count()
```

### Node 関連

```python
class ParentEdgeSerializer(serializers.Serializer):
    """親エッジ情報"""
    parent_id = serializers.UUIDField(source="parent.id")
    parent_sfen = serializers.CharField(source="parent.sfen")
    move_usi = serializers.CharField()
    move_japanese = serializers.CharField()


class ChildNodeSerializer(serializers.Serializer):
    """子ノード情報（エッジ付き）"""
    node = NodeSerializer()
    move_usi = serializers.CharField()
    move_japanese = serializers.CharField()


class NodeDetailSerializer(serializers.ModelSerializer):
    """ノード詳細出力（親子情報付き）"""
    is_root = serializers.BooleanField(read_only=True)
    parents = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()

    class Meta:
        model = Node
        fields = [
            "id", "tree_id", "sfen", "ply", "comment", "evaluation",
            "metadata", "is_root", "created_at", "updated_at",
            "parents", "children"
        ]

    def get_parents(self, obj):
        edges = obj.parent_edges.select_related("parent").all()
        return ParentEdgeSerializer(edges, many=True).data

    def get_children(self, obj):
        edges = obj.child_edges.select_related("child").all()
        return [
            {
                "node": NodeSerializer(edge.child).data,
                "move_usi": edge.move_usi,
                "move_japanese": edge.move_japanese,
            }
            for edge in edges
        ]
```

### Move 関連

```python
class MoveCreateSerializer(serializers.Serializer):
    """POST /nodes/{id}/moves 入力"""
    move_usi = serializers.RegexField(
        regex=r'^[1-9][a-i][1-9][a-i](\+)?$|^[PLNSGBR]\*[1-9][a-i]$',
        max_length=10,
        error_messages={
            "invalid": "指し手はUSI形式で入力してください（例: 7g7f, P*5e）"
        }
    )


class EdgeSerializer(serializers.ModelSerializer):
    """エッジ出力"""
    class Meta:
        model = Edge
        fields = ["id", "move_usi", "move_japanese"]


class MoveResultSerializer(serializers.Serializer):
    """POST /nodes/{id}/moves 出力"""
    edge = EdgeSerializer()
    child_node = NodeSerializer()
    is_transposition = serializers.BooleanField()
```

---

## エラーレスポンス形式

OpenAPI 定義（MoveError スキーマ）に準拠:

```python
class MoveErrorSerializer(serializers.Serializer):
    """エラー出力"""
    error = serializers.ChoiceField(choices=[
        "illegal_move", "nifu", "uchifuzume", "invalid_format"
    ])
    message = serializers.CharField()
    move_usi = serializers.CharField(required=False)
```

---

## 参照

- [004-joseki-manager-phase2/data-model.md](../004-joseki-manager-phase2/data-model.md) - Phase 2 データモデル
- [002-joseki-manager/contracts/openapi.yaml](../002-joseki-manager/contracts/openapi.yaml) - API スキーマ定義
