# Data Model: Phase 2 - コアインフラ構築

**Feature**: 004-joseki-manager-phase2
**Date**: 2026-01-16
**Status**: Draft
**Base**: [002-joseki-manager/data-model.md](../002-joseki-manager/data-model.md)

## 概要

このドキュメントは 002-joseki-manager の data-model.md を基に、Phase 2 の明確化決定事項（CD-001〜CD-005）を反映した更新版です。

## 明確化による変更点

| 決定 | 変更内容 |
|------|----------|
| CD-003 | Node に `ply` フィールドを追加 |
| CD-004 | Node に `sfen_with_ply` property を追加 |
| CD-005 | Edge.move_japanese を NULLABLE に変更 |

---

## Entity Relationship Diagram

```
┌─────────────────┐       ┌─────────────────┐
│   JosekiTree    │       │      Label      │
├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │
│ name            │       │ name (UNIQUE)   │
│ description     │       │ color           │
│ created_at      │       │ description     │
│ updated_at      │       │ created_at      │
│ is_deleted      │       └────────┬────────┘
│ deleted_at      │                │
└────────┬────────┘                │
         │                         │
         │ 1:N                     │ M:N
         │                         │
         ▼                         │
┌─────────────────┐       ┌────────┴────────┐
│      Node       │◄──────┤    NodeLabel    │
├─────────────────┤       ├─────────────────┤
│ id (PK)         │       │ id (PK)         │
│ tree_id (FK)    │       │ node_id (FK)    │
│ sfen            │       │ label_id (FK)   │
│ ply [NEW]       │       │ created_at      │
│ comment         │       └─────────────────┘
│ evaluation      │
│ metadata (JSON) │
│ created_at      │
│ updated_at      │
└────────┬────────┘
         │
         │ M:N (via Edge)
         │
         ▼
┌─────────────────┐
│      Edge       │
├─────────────────┤
│ id (PK)         │
│ parent_id (FK)  │
│ child_id (FK)   │
│ move_usi        │
│ move_japanese   │ ← NULLABLE (CD-005)
│ created_at      │
└─────────────────┘
```

---

## Entities

### JosekiTree（定跡ツリー）

*002-joseki-manager/data-model.md から変更なし*

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | 一意識別子 |
| name | VARCHAR(200) | NOT NULL | ツリー名 |
| description | TEXT | NULLABLE | 説明文 |
| created_at | TIMESTAMP | NOT NULL, AUTO | 作成日時 |
| updated_at | TIMESTAMP | NOT NULL, AUTO | 更新日時 |
| is_deleted | BOOLEAN | DEFAULT FALSE | ソフトデリートフラグ |
| deleted_at | TIMESTAMP | NULLABLE | 削除日時 |

**Indexes**:
- `idx_tree_is_deleted` on (is_deleted)
- `idx_tree_deleted_at` on (deleted_at)

---

### Node（ノード）

**変更点（CD-003, CD-004）**: `ply` フィールドと `sfen_with_ply` property を追加

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | 一意識別子 |
| tree_id | UUID | FK(JosekiTree), NOT NULL | 所属ツリー |
| sfen | VARCHAR(200) | NOT NULL | 局面（SFEN形式、**手数除く**） |
| **ply** | INTEGER | DEFAULT 0 | **手数（0=初期局面）** [NEW] |
| comment | TEXT | NULLABLE | ユーザーコメント |
| evaluation | INTEGER | NULLABLE | 局面評価値（centipawn単位） |
| metadata | JSONB | DEFAULT '{}' | 拡張用メタデータ |
| created_at | TIMESTAMP | NOT NULL, AUTO | 作成日時 |
| updated_at | TIMESTAMP | NOT NULL, AUTO | 更新日時 |

**Indexes**:
- `idx_node_tree_sfen` on (tree_id, sfen) - UNIQUE
- `idx_node_sfen` on (sfen) - 転置検索用

**Validation**:
- sfen: 有効なSFEN形式（手数なし、cshogi で検証）
- ply: 0 以上の整数
- evaluation: -99999 〜 +99999

**Property**:
- `sfen_with_ply`: 手数を含む SFEN を返す（`f"{self.sfen} {self.ply}"`）

---

### Edge（エッジ）

**変更点（CD-005）**: `move_japanese` を NULLABLE に変更

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | 一意識別子 |
| parent_id | UUID | FK(Node), NOT NULL | 親ノード |
| child_id | UUID | FK(Node), NOT NULL | 子ノード |
| move_usi | VARCHAR(10) | NOT NULL | USI形式の指し手 |
| move_japanese | VARCHAR(20) | **NULLABLE** | 日本語表記（後から生成可能） |
| created_at | TIMESTAMP | NOT NULL, AUTO | 作成日時 |

**Indexes**:
- `idx_edge_parent_move` on (parent_id, move_usi) - UNIQUE
- `idx_edge_child` on (child_id) - 逆引き用

**Constraints**:
- parent と child は同一ツリーに属すること
- parent_id ≠ child_id（自己参照禁止）

---

### Label（ラベル）

*002-joseki-manager/data-model.md から変更なし*

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | 一意識別子 |
| name | VARCHAR(100) | UNIQUE, NOT NULL | ラベル名 |
| color | VARCHAR(7) | NULLABLE | 表示色（HEX形式） |
| description | TEXT | NULLABLE | ラベルの説明 |
| created_at | TIMESTAMP | NOT NULL, AUTO | 作成日時 |

---

### NodeLabel（ノード-ラベル関連）

*002-joseki-manager/data-model.md から変更なし*

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | 一意識別子 |
| node_id | UUID | FK(Node), NOT NULL | ノード |
| label_id | UUID | FK(Label), NOT NULL | ラベル |
| created_at | TIMESTAMP | NOT NULL, AUTO | 作成日時 |

**Indexes**:
- `idx_nodelabel_node_label` on (node_id, label_id) - UNIQUE
- `idx_nodelabel_label` on (label_id) - ラベル検索用

---

## Django Models（更新版）

```python
import uuid
from django.db import models
from django.core.validators import RegexValidator


class JosekiTree(models.Model):
    """定跡ツリー"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False, db_index=True)
    deleted_at = models.DateTimeField(null=True, blank=True, db_index=True)

    class Meta:
        db_table = 'joseki_trees'
        ordering = ['-updated_at']

    def __str__(self):
        return self.name


class Node(models.Model):
    """ノード（局面）"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tree = models.ForeignKey(
        JosekiTree,
        on_delete=models.CASCADE,
        related_name='nodes'
    )
    sfen = models.CharField(max_length=200, db_index=True)
    ply = models.IntegerField(default=0, help_text='手数（0=初期局面）')  # CD-003
    comment = models.TextField(blank=True)
    evaluation = models.IntegerField(
        null=True,
        blank=True,
        help_text='局面評価値（centipawn単位）'
    )
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'nodes'
        constraints = [
            models.UniqueConstraint(
                fields=['tree', 'sfen'],
                name='unique_node_per_tree_position'
            )
        ]

    def __str__(self):
        return f'{self.tree.name}: {self.sfen[:30]}...'

    @property
    def is_root(self):
        """ルートノードかどうか"""
        return not self.parent_edges.exists()

    @property
    def sfen_with_ply(self) -> str:
        """手数を含む SFEN を返す（CD-004）"""
        return f"{self.sfen} {self.ply}"


class Edge(models.Model):
    """エッジ（指し手）"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    parent = models.ForeignKey(
        Node,
        on_delete=models.CASCADE,
        related_name='child_edges'
    )
    child = models.ForeignKey(
        Node,
        on_delete=models.CASCADE,
        related_name='parent_edges'
    )
    move_usi = models.CharField(max_length=10)
    move_japanese = models.CharField(max_length=20, blank=True)  # CD-005: NULLABLE
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'edges'
        constraints = [
            models.UniqueConstraint(
                fields=['parent', 'move_usi'],
                name='unique_move_from_parent'
            ),
            models.CheckConstraint(
                check=~models.Q(parent=models.F('child')),
                name='no_self_reference'
            )
        ]

    def __str__(self):
        return f'{self.move_usi} ({self.move_japanese})'


class Label(models.Model):
    """ラベル（戦型タグ）"""
    HEX_COLOR_VALIDATOR = RegexValidator(
        regex=r'^#[0-9A-Fa-f]{6}$',
        message='色は #RRGGBB 形式で指定してください'
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True)
    color = models.CharField(
        max_length=7,
        blank=True,
        validators=[HEX_COLOR_VALIDATOR]
    )
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'labels'
        ordering = ['name']

    def __str__(self):
        return self.name


class NodeLabel(models.Model):
    """ノード-ラベル関連"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    node = models.ForeignKey(
        Node,
        on_delete=models.CASCADE,
        related_name='node_labels'
    )
    label = models.ForeignKey(
        Label,
        on_delete=models.CASCADE,
        related_name='node_labels'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'node_labels'
        constraints = [
            models.UniqueConstraint(
                fields=['node', 'label'],
                name='unique_label_per_node'
            )
        ]

    def __str__(self):
        return f'{self.node} - {self.label}'
```

---

## 参照

- [002-joseki-manager/data-model.md](../002-joseki-manager/data-model.md) - 元のデータモデル定義
- [004-joseki-manager-phase2/spec.md](./spec.md) - Phase 2 仕様書（明確化決定事項を含む）
