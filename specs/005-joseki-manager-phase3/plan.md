# Implementation Plan: Phase 3 - 定跡ツリーの作成と手順入力 (MVP)

**Branch**: `005-joseki-manager-phase3` | **Date**: 2026-01-16 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/005-joseki-manager-phase3/spec.md`

## Summary

将棋定跡管理アプリケーション（Joseki Manager）の **MVP（最小限の価値を提供する製品）** を実装する。定跡ツリーの CRUD、指し手追加、転置検出、反則手拒否の API を Django REST Framework で構築する。Phase 2 で構築済みのモデルとcshogi統合を活用し、Service層とViewSet を TDD で実装する。

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: Django 5.0+, Django REST Framework 3.14+, cshogi 0.8+
**Storage**: PostgreSQL 15+
**Testing**: pytest, pytest-django, factory_boy
**Target Platform**: Linux/macOS/Windows（ローカルサーバー）
**Project Type**: Single project（REST API バックエンド）
**Performance Goals**: 100ノード以上のツリーで API 応答 1秒以内（SC-003）
**Constraints**: シングルユーザー、認証なし、ローカル実行
**Scale/Scope**: 定跡ツリー数十個、ノード数千〜数万規模

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| 原則 | 状態 | 対応 |
|------|------|------|
| I. 日本語ドキュメンテーション | ✅ Pass | すべての技術文書を日本語で作成 |
| II. シンプルさ優先 | ✅ Pass | 最小限の API から開始、過度な抽象化なし |
| III. 明確なコミュニケーション | ✅ Pass | エラーレスポンスは OpenAPI 定義に準拠 |
| IV. ブランチ運用ポリシー | ✅ Pass | `005-joseki-manager-phase3` ブランチで作業 |
| V. テスト駆動開発（TDD） | ✅ Pass | Contract/Integration テストを先に作成 |

**判定**: すべてのゲートをパス。

---

## Project Structure

### Documentation (this feature)

```text
specs/005-joseki-manager-phase3/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0: Technical research
├── data-model.md        # Phase 1: Service/Serializer design
├── quickstart.md        # Phase 1: Development guide
├── contracts/           # Phase 1: API contracts
│   └── openapi-phase3.md
└── checklists/          # Quality checklists
    └── requirements.md
```

### Source Code (repository root)

```text
src/
├── joseki/                    # Django project (Phase 1 で作成済み)
│   ├── settings.py
│   └── urls.py                # UPDATE: trees URL 登録
├── trees/                     # 定跡ツリー管理アプリ
│   ├── models.py              # Phase 2 で実装済み
│   ├── serializers.py         # NEW [Phase 3]
│   ├── views.py               # NEW [Phase 3]
│   ├── urls.py                # NEW [Phase 3]
│   └── services/              # NEW [Phase 3]
│       ├── __init__.py
│       ├── tree_service.py
│       └── node_service.py
├── labels/                    # Phase 2 で作成済み
├── exports/                   # Phase 2 で作成済み
└── core/                      # Phase 2 で実装済み
    └── shogi/
        ├── position.py
        ├── rules.py
        └── exceptions.py

tests/
├── conftest.py                # Phase 1 で作成済み
├── factories.py               # Phase 2 で作成済み
├── unit/                      # Phase 2 で作成済み
├── contract/                  # NEW [Phase 3]
│   ├── test_trees_api.py
│   └── test_nodes_api.py
└── integration/               # NEW [Phase 3]
    └── test_tree_workflow.py
```

**Structure Decision**: Phase 2 の構造を継承。Service 層を `services/` ディレクトリに追加し、ViewSet を `views.py` に実装。

---

## Complexity Tracking

> **該当なし**: Constitution Check に違反がないため、複雑さの正当化は不要。

---

## Design Decisions

### 1. Service Layer パターン（RQ-002）

**決定**: ViewSet → Service → Model の3層構造

**理由**:
- ビジネスロジック（転置検出、合法手検証）を Service 層に集約
- ViewSet は HTTP リクエスト/レスポンスのみを担当
- テスタビリティの向上

### 2. 転置検出アルゴリズム（RQ-003）

**決定**: SFEN による同一局面検索

**理由**:
- Node.sfen フィールドには手数なし SFEN が格納済み
- UNIQUE 制約 (tree, sfen) があるため効率的に検索可能

### 3. URL ルーティング（RQ-005）

**決定**: DefaultRouter + 手動ルーティング

**理由**:
- ネストしたリソースは手動でルーティング
- シンプルさを優先

### 4. Serializer 設計（RQ-007）

**決定**: 読み取り/書き込み用 Serializer を分離

**理由**:
- 入力と出力で必要なフィールドが異なる
- OpenAPI 定義に準拠

---

## Implementation Phases

### Phase 3.1: Contract Tests（TDD - Red）

1. `tests/contract/test_trees_api.py` を作成
   - POST /trees テスト（T036）
   - GET /trees/{id} テスト（T037）
   - GET /trees テスト（T038）
   - PATCH /trees/{id} テスト（T039）

2. `tests/contract/test_nodes_api.py` を作成
   - POST /nodes/{id}/moves テスト（T040）
   - GET /nodes/{id}/children テスト（T041）
   - DELETE /nodes/{id} テスト（T041b）

### Phase 3.2: Integration Tests（TDD - Red）

1. `tests/integration/test_tree_workflow.py` を作成
   - ツリー作成+ルートノードテスト（T042）
   - 指し手追加・分岐テスト（T043）
   - 転置検出テスト（T044）
   - 反則手拒否テスト（T045）
   - 転置ノード削除テスト（T045b）

### Phase 3.3: Serializers 実装

1. JosekiTreeCreateSerializer, JosekiTreeUpdateSerializer（T046）
2. NodeSerializer, NodeDetailSerializer（T047）
3. EdgeSerializer（T048）
4. MoveCreateSerializer, MoveResultSerializer（T049）

### Phase 3.4: Services 実装

1. TreeService（T050）
   - create_tree: ツリー作成 + ルートノード自動作成
   - get_tree, list_trees, update_tree

2. NodeService（T051）
   - add_move: 指し手追加 + 転置検出
   - get_children: 子ノード取得
   - delete_node: ノード削除（単一親/転置対応）

### Phase 3.5: ViewSets 実装

1. JosekiTreeViewSet（T052）
   - list, create, retrieve, partial_update

2. NodeViewSet（T053）
   - retrieve, destroy
   - add_move（@action）
   - children（@action）

### Phase 3.6: URL Routing

1. `src/trees/urls.py` を作成（T054）
2. `src/joseki/urls.py` を更新（T055）

### Phase 3.7: テスト検証

1. 全 Contract Tests がパスすることを確認（T056）
2. 全 Integration Tests がパスすることを確認（T057）

---

## Success Criteria

Phase 3 の完了条件（spec.md より）:

- [ ] SC-001: 全 Contract Tests がパスする
- [ ] SC-002: 全 Integration Tests がパスする
- [ ] SC-003: 100ノード以上のツリーで API 応答 1秒以内
- [ ] SC-004: 定跡ツリーの CRUD 操作ができる
- [ ] SC-005: 合法手のみが追加できる（反則手は拒否）
- [ ] SC-006: 転置（同一局面）が検出される
- [ ] SC-007: ノード削除が正しく動作する

---

## Task Summary

| Phase | Tasks | Description |
|-------|-------|-------------|
| 3.1 | T036-T041b | Contract Tests（Red） |
| 3.2 | T042-T045b | Integration Tests（Red） |
| 3.3 | T046-T049 | Serializers 実装 |
| 3.4 | T050-T051 | Services 実装 |
| 3.5 | T052-T053 | ViewSets 実装 |
| 3.6 | T054-T055 | URL Routing |
| 3.7 | T056-T057 | テスト検証（Green） |

**合計**: 22 タスク

---

## Next Steps

1. `/speckit.tasks` - 詳細タスク一覧を生成（tasks.md）
2. `/speckit.implement` - 実装を開始

---

## References

- [spec.md](./spec.md) - Phase 3 仕様書
- [research.md](./research.md) - 技術調査
- [data-model.md](./data-model.md) - Service/Serializer 設計
- [quickstart.md](./quickstart.md) - 開発ガイド
- [002-joseki-manager/contracts/openapi.yaml](../002-joseki-manager/contracts/openapi.yaml) - API 仕様
- [002-joseki-manager/tasks.md](../002-joseki-manager/tasks.md) - 全体タスク一覧
- [004-joseki-manager-phase2/](../004-joseki-manager-phase2/) - Phase 2 成果物
