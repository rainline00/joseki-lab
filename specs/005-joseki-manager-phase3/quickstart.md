# Quickstart: Phase 3 - 定跡ツリーの作成と手順入力 (MVP)

**Feature**: 005-joseki-manager-phase3
**Date**: 2026-01-16

## 前提条件

Phase 2 が完了していること:
- Django プロジェクトが設定済み
- モデル（JosekiTree, Node, Edge）が実装済み
- cshogi 統合が完了

## 開発環境セットアップ

### 1. 依存関係のインストール

```bash
cd /path/to/joseki-lab
uv sync
```

### 2. データベース起動

```bash
docker compose up -d db
```

### 3. マイグレーション適用（Phase 2 で実施済み）

```bash
uv run python src/manage.py migrate
```

### 4. 開発サーバー起動

```bash
uv run python src/manage.py runserver
```

---

## Phase 3 実装の流れ

### TDD サイクル（Red-Green-Refactor）

1. **Red Phase**: Contract Tests と Integration Tests を書く（失敗を確認）
2. **Green Phase**: 実装を行いテストをパスさせる
3. **Refactor Phase**: コードをリファクタリング

### 実装順序

1. Contract Tests を作成（T036-T041b）
2. Integration Tests を作成（T042-T045b）
3. Serializers を実装（T046-T049）
4. Services を実装（T050-T051）
5. ViewSets を実装（T052-T053）
6. URL routing を設定（T054-T055）
7. テストが全てパスすることを確認（T056-T057）

---

## テスト実行

### 全テスト実行

```bash
uv run pytest
```

### Phase 3 のテストのみ

```bash
# Contract Tests
uv run pytest tests/contract/test_trees_api.py tests/contract/test_nodes_api.py -v

# Integration Tests
uv run pytest tests/integration/test_tree_workflow.py -v
```

### カバレッジ付き

```bash
uv run pytest --cov=src --cov-report=html
open htmlcov/index.html
```

---

## API 動作確認

### 定跡ツリー作成

```bash
curl -X POST http://localhost:8000/api/v1/trees/ \
  -H "Content-Type: application/json" \
  -d '{"name": "矢倉"}'
```

期待されるレスポンス（201 Created）:
```json
{
  "id": "uuid",
  "name": "矢倉",
  "description": "",
  "node_count": 1,
  "root_node": {
    "id": "uuid",
    "sfen": "lnsgkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL b -",
    "ply": 0,
    "is_root": true
  },
  ...
}
```

### 指し手追加

```bash
# {tree_id} と {node_id} は作成時のレスポンスから取得
curl -X POST http://localhost:8000/api/v1/trees/{tree_id}/nodes/{node_id}/moves/ \
  -H "Content-Type: application/json" \
  -d '{"move_usi": "7g7f"}'
```

期待されるレスポンス（201 Created）:
```json
{
  "edge": {
    "id": "uuid",
    "move_usi": "7g7f",
    "move_japanese": ""
  },
  "child_node": {
    "id": "uuid",
    "sfen": "lnsgkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL w - 1",
    "ply": 1,
    "is_root": false
  },
  "is_transposition": false
}
```

### 反則手テスト

```bash
# 不正な指し手形式
curl -X POST http://localhost:8000/api/v1/trees/{tree_id}/nodes/{node_id}/moves/ \
  -H "Content-Type: application/json" \
  -d '{"move_usi": "invalid"}'
```

期待されるレスポンス（400 Bad Request）:
```json
{
  "error": "invalid_format",
  "message": "指し手はUSI形式で入力してください（例: 7g7f, P*5e）",
  "move_usi": "invalid"
}
```

---

## ファイル構成

Phase 3 で作成/更新するファイル:

```
src/
├── trees/
│   ├── serializers.py       # NEW: Serializers
│   ├── views.py             # NEW: ViewSets
│   ├── urls.py              # NEW: URL routing
│   └── services/
│       ├── __init__.py      # NEW
│       ├── tree_service.py  # NEW: TreeService
│       └── node_service.py  # NEW: NodeService
└── joseki/
    └── urls.py              # UPDATE: trees URL 登録

tests/
├── contract/
│   ├── test_trees_api.py    # NEW: Trees API contract tests
│   └── test_nodes_api.py    # NEW: Nodes API contract tests
└── integration/
    └── test_tree_workflow.py # NEW: Workflow integration tests
```

---

## トラブルシューティング

### cshogi インポートエラー

```bash
# cshogi が正しくインストールされているか確認
uv run python -c "import cshogi; print(cshogi.__version__)"
```

### データベース接続エラー

```bash
# PostgreSQL が起動しているか確認
docker compose ps

# 接続テスト
uv run python src/manage.py dbshell
```

### テスト失敗時

```bash
# 詳細出力でテスト実行
uv run pytest -v --tb=long

# 特定のテストのみ実行
uv run pytest tests/contract/test_trees_api.py::test_create_tree -v
```

---

## 参照

- [spec.md](./spec.md) - Phase 3 仕様書
- [research.md](./research.md) - 技術調査
- [data-model.md](./data-model.md) - データモデル・サービス設計
- [002-joseki-manager/contracts/openapi.yaml](../002-joseki-manager/contracts/openapi.yaml) - API 仕様
