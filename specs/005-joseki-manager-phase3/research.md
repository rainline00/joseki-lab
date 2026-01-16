# Research: Phase 3 - 定跡ツリーの作成と手順入力 (MVP)

**Feature**: 005-joseki-manager-phase3
**Date**: 2026-01-16
**Status**: Complete

## 概要

Phase 3 の実装に必要な技術調査結果をまとめる。Phase 2 で基盤が構築済みのため、主に API 実装パターンと DRF の使用方法に焦点を当てる。

---

## 調査項目

### RQ-001: Django REST Framework ViewSet パターン

**決定**: ModelViewSet + カスタムアクション

**理由**:
- 標準的な CRUD 操作には ModelViewSet が最適
- カスタムエンドポイント（/moves, /children）には `@action` デコレータを使用
- DRF の規約に従うことで、メンテナンス性と一貫性を確保

**実装パターン**:
```python
class JosekiTreeViewSet(viewsets.ModelViewSet):
    queryset = JosekiTree.objects.filter(is_deleted=False)
    serializer_class = JosekiTreeSerializer

class NodeViewSet(viewsets.GenericViewSet):
    queryset = Node.objects.all()

    @action(detail=True, methods=['post'])
    def moves(self, request, pk=None):
        """POST /nodes/{id}/moves/"""
        pass

    @action(detail=True, methods=['get'])
    def children(self, request, pk=None):
        """GET /nodes/{id}/children/"""
        pass
```

---

### RQ-002: Service Layer パターン

**決定**: ViewSet → Service → Model の3層構造

**理由**:
- ビジネスロジック（転置検出、合法手検証）を Service 層に集約
- ViewSet は HTTP リクエスト/レスポンスのみを担当
- テスタビリティの向上（Service 単体でテスト可能）

**Service 構成**:
- `TreeService`: ツリー CRUD + ルートノード自動作成
- `NodeService`: 指し手追加、転置検出、ノード削除

---

### RQ-003: 転置検出アルゴリズム

**決定**: SFEN による同一局面検索

**理由**:
- Node.sfen フィールドには手数なし SFEN が格納済み（Phase 2）
- 同一ツリー内で SFEN が一致するノードを検索すれば転置を検出可能
- UNIQUE 制約 (tree, sfen) があるため、重複ノードは発生しない

**実装**:
```python
def add_move(self, parent_node: Node, move_usi: str) -> tuple[Node, Edge, bool]:
    """
    Returns:
        tuple: (child_node, edge, is_transposition)
    """
    new_sfen = apply_move(parent_node.sfen, move_usi)

    # 転置検出
    existing_node = Node.objects.filter(
        tree=parent_node.tree,
        sfen=new_sfen
    ).first()

    if existing_node:
        # 転置: 既存ノードへエッジを作成
        edge = Edge.objects.create(
            parent=parent_node,
            child=existing_node,
            move_usi=move_usi
        )
        return existing_node, edge, True
    else:
        # 新規ノード作成
        new_node = Node.objects.create(
            tree=parent_node.tree,
            sfen=new_sfen,
            ply=parent_node.ply + 1
        )
        edge = Edge.objects.create(
            parent=parent_node,
            child=new_node,
            move_usi=move_usi
        )
        return new_node, edge, False
```

---

### RQ-004: エラーハンドリング戦略

**決定**: カスタム例外 + DRF 例外ハンドラ

**理由**:
- Phase 2 で定義済みの例外（IllegalMoveError, InvalidMoveError）を活用
- DRF の標準例外ハンドリング機構と統合
- エラーレスポンスは OpenAPI 定義（MoveError スキーマ）に準拠

**エラーコード**:
| 例外 | error コード | HTTP Status |
|------|-------------|-------------|
| InvalidMoveError | invalid_format | 400 |
| IllegalMoveError | illegal_move | 400 |
| 二歩検出 | nifu | 400 |
| 打ち歩詰め | uchifuzume | 400 |
| 重複指し手 | duplicate_move | 409 |

---

### RQ-005: URL ルーティング設計

**決定**: Nested Router を使用しない

**理由**:
- DRF の DefaultRouter で基本的な CRUD は対応
- ネストしたリソース（/trees/{id}/nodes/{id}/moves）は手動でルーティング
- シンプルさを優先（Constitution II に従う）

**URL 構成**:
```python
# src/trees/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'trees', JosekiTreeViewSet, basename='tree')

urlpatterns = [
    path('', include(router.urls)),
    # カスタムルーティング
    path('trees/<uuid:tree_id>/nodes/<uuid:node_id>/moves/',
         NodeViewSet.as_view({'post': 'add_move'}), name='node-add-move'),
    path('trees/<uuid:tree_id>/nodes/<uuid:node_id>/children/',
         NodeViewSet.as_view({'get': 'children'}), name='node-children'),
    path('trees/<uuid:tree_id>/nodes/<uuid:node_id>/',
         NodeViewSet.as_view({'get': 'retrieve', 'delete': 'destroy'}), name='node-detail'),
]
```

---

### RQ-006: ノード削除のトランザクション管理

**決定**: Django ORM の CASCADE 削除 + トランザクション

**理由**:
- Edge モデルは `on_delete=CASCADE` で定義済み
- 転置ノードのエッジ削除には手動処理が必要
- 整合性保証のため `@transaction.atomic` を使用

**実装**:
```python
@transaction.atomic
def delete_node(self, node: Node, parent_id: uuid.UUID | None = None) -> None:
    if node.is_root:
        raise ValueError("ルートノードは削除できません")

    parent_edges = node.parent_edges.all()

    if parent_edges.count() > 1:
        # 転置ノード: parent_id 必須
        if parent_id is None:
            raise ValueError("転置ノードの削除には parent_id が必要です")
        edge = parent_edges.filter(parent_id=parent_id).first()
        if edge is None:
            raise ValueError("指定された親からのエッジが見つかりません")
        edge.delete()
    else:
        # 単一親ノード: 子孫含め削除（CASCADE で自動処理）
        node.delete()
```

---

### RQ-007: Serializer 設計

**決定**: 読み取り/書き込み用 Serializer を分離

**理由**:
- 入力（Create/Update）と出力（Response）で必要なフィールドが異なる
- OpenAPI 定義に準拠したレスポンス形式を確保
- DRF のベストプラクティスに従う

**Serializer 一覧**:
| Serializer | 用途 |
|------------|------|
| JosekiTreeCreateSerializer | POST /trees 入力 |
| JosekiTreeUpdateSerializer | PATCH /trees/{id} 入力 |
| JosekiTreeSerializer | GET /trees, /trees/{id} 出力 |
| JosekiTreeSummarySerializer | GET /trees 一覧出力 |
| NodeSerializer | ノード出力（基本） |
| NodeDetailSerializer | ノード出力（詳細 + 親子情報） |
| MoveCreateSerializer | POST /nodes/{id}/moves 入力 |
| MoveResultSerializer | POST /nodes/{id}/moves 出力 |
| ChildNodeSerializer | GET /nodes/{id}/children 出力 |

---

## 未解決事項

なし（すべての調査項目が解決済み）

---

## 参照

- [Django REST Framework Documentation](https://www.django-rest-framework.org/)
- [002-joseki-manager/contracts/openapi.yaml](../002-joseki-manager/contracts/openapi.yaml)
- [004-joseki-manager-phase2/research.md](../004-joseki-manager-phase2/research.md) - Phase 2 調査結果
