# Data Model: 将棋定跡管理アプリケーション

**Feature**: 002-joseki-manager
**Date**: 2026-01-12
**Status**: Draft

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
│ comment         │       │ created_at      │
│ evaluation      │       └─────────────────┘
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
│ move_japanese   │
│ created_at      │
└─────────────────┘
```

## Entities

### JosekiTree（定跡ツリー）

1つの定跡体系を表すルートエンティティ。

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | 一意識別子 |
| name | VARCHAR(200) | NOT NULL | ツリー名（例：「矢倉」「四間飛車」） |
| description | TEXT | NULLABLE | 説明文 |
| created_at | TIMESTAMP | NOT NULL, AUTO | 作成日時 |
| updated_at | TIMESTAMP | NOT NULL, AUTO | 更新日時 |
| is_deleted | BOOLEAN | DEFAULT FALSE | ソフトデリートフラグ |
| deleted_at | TIMESTAMP | NULLABLE | 削除日時（ゴミ箱移動時） |

**Indexes**:
- `idx_tree_is_deleted` on (is_deleted)
- `idx_tree_deleted_at` on (deleted_at)

**Validation**:
- name: 1-200文字

---

### Node（ノード）

定跡ツリー内の各局面を表すノード。

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | 一意識別子 |
| tree_id | UUID | FK(JosekiTree), NOT NULL | 所属ツリー |
| sfen | VARCHAR(200) | NOT NULL | 局面（SFEN形式、手数除く） |
| comment | TEXT | NULLABLE | ユーザーコメント |
| evaluation | INTEGER | NULLABLE | 局面評価値（将来のUSI連携用、centipawn単位） |
| metadata | JSONB | DEFAULT '{}' | 拡張用メタデータ |
| created_at | TIMESTAMP | NOT NULL, AUTO | 作成日時 |
| updated_at | TIMESTAMP | NOT NULL, AUTO | 更新日時 |

**Indexes**:
- `idx_node_tree_sfen` on (tree_id, sfen) - UNIQUE
- `idx_node_sfen` on (sfen) - 転置検索用

**Validation**:
- sfen: 有効なSFEN形式（cshogi で検証）
- evaluation: -99999 〜 +99999（mate score対応）

**metadata フィールドの想定用途**:

```json
{
  "source": "棋書名や出典",
  "frequency": 0.85,           // 出現頻度（将来の統計機能用）
  "engine_depth": 30,          // 評価時の探索深さ
  "engine_name": "YaneuraOu",  // 評価エンジン名
  "custom_tags": ["急戦", "持久戦"],
  "references": [              // 参考棋譜
    {
      "black": "羽生善治",
      "white": "藤井聡太",
      "date": "2024-01-15",
      "result": "先手勝ち"
    }
  ]
}
```

---

### Edge（エッジ）

親ノードから子ノードへの遷移（指し手）を表す。

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | 一意識別子 |
| parent_id | UUID | FK(Node), NOT NULL | 親ノード |
| child_id | UUID | FK(Node), NOT NULL | 子ノード |
| move_usi | VARCHAR(10) | NOT NULL | USI形式の指し手（例：`7g7f`） |
| move_japanese | VARCHAR(20) | NULLABLE | 日本語表記（例：`７六歩`） |
| created_at | TIMESTAMP | NOT NULL, AUTO | 作成日時 |

**Indexes**:
- `idx_edge_parent_move` on (parent_id, move_usi) - UNIQUE
- `idx_edge_child` on (child_id) - 逆引き用

**Constraints**:
- parent と child は同一ツリーに属すること
- parent_id ≠ child_id（自己参照禁止）

**Validation**:
- move_usi: 有効なUSI形式（cshogi で検証）

---

### Label（ラベル）

戦型や任意の分類を表すタグ。グローバル定義。

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | UUID | PK | 一意識別子 |
| name | VARCHAR(100) | UNIQUE, NOT NULL | ラベル名（例：「矢倉」「角換わり」） |
| color | VARCHAR(7) | NULLABLE | 表示色（HEX形式：`#FF0000`） |
| description | TEXT | NULLABLE | ラベルの説明 |
| created_at | TIMESTAMP | NOT NULL, AUTO | 作成日時 |

**Indexes**:
- `idx_label_name` on (name) - UNIQUE

**Validation**:
- name: 1-100文字
- color: `#[0-9A-Fa-f]{6}` 形式

---

### NodeLabel（ノード-ラベル関連）

ノードとラベルの多対多関連。

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

## State Transitions

### JosekiTree のライフサイクル

```
┌──────────┐      delete()       ┌──────────┐
│  Active  │ ──────────────────► │  Trash   │
│          │                     │          │
│is_deleted│ ◄────────────────── │is_deleted│
│ = false  │     restore()       │ = true   │
└──────────┘                     └────┬─────┘
                                      │
                                      │ permanent_delete()
                                      │ または
                                      │ 30日経過（自動）
                                      ▼
                                 ┌──────────┐
                                 │ Deleted  │
                                 │(物理削除)│
                                 └──────────┘
```

### Node の作成フロー

```
1. 指し手を受信
2. cshogi で合法性検証
   - 不正 → エラー返却
3. 指し手を適用して新局面のSFENを取得
4. 同一ツリー内で同一SFENのNodeを検索
   - 存在する → 既存Nodeを使用（転置）
   - 存在しない → 新規Node作成
5. Edgeを作成（parent → child）
```

---

## Django Models

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
    move_japanese = models.CharField(max_length=20, blank=True)
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

## Query Patterns

### 1. ツリー全体の取得（深さ制限付き）

```python
def get_tree_nodes(tree_id: uuid.UUID, max_depth: int = 10):
    """ツリーのノードを階層的に取得"""
    root_nodes = Node.objects.filter(
        tree_id=tree_id
    ).exclude(
        parent_edges__isnull=False
    ).prefetch_related(
        Prefetch('child_edges', queryset=Edge.objects.select_related('child')),
        'node_labels__label'
    )
    return root_nodes
```

### 2. ラベルによるノード検索

```python
def search_nodes_by_label(label_id: uuid.UUID):
    """特定ラベルが付いたノードを検索"""
    return Node.objects.filter(
        node_labels__label_id=label_id
    ).select_related('tree').prefetch_related('node_labels__label')
```

### 3. 転置検出

```python
def find_transposition(tree_id: uuid.UUID, sfen: str) -> Node | None:
    """同一局面のノードが既に存在するか確認"""
    try:
        return Node.objects.get(tree_id=tree_id, sfen=sfen)
    except Node.DoesNotExist:
        return None
```

### 4. 子ノード一覧取得

```python
def get_children(node_id: uuid.UUID):
    """ノードの子ノードを取得"""
    return Edge.objects.filter(
        parent_id=node_id
    ).select_related('child').prefetch_related(
        'child__node_labels__label'
    )
```
