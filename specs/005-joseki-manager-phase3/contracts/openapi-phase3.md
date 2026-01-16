# API Contracts: Phase 3

**Feature**: 005-joseki-manager-phase3
**Date**: 2026-01-16
**Base**: [002-joseki-manager/contracts/openapi.yaml](../../002-joseki-manager/contracts/openapi.yaml)

## 概要

Phase 3 で実装する API エンドポイントの抜粋。完全な定義は [openapi.yaml](../../002-joseki-manager/contracts/openapi.yaml) を参照。

---

## エンドポイント一覧

### Trees

| Method | Path | Description | Status Codes |
|--------|------|-------------|--------------|
| POST | /trees | 定跡ツリー作成 | 201, 400 |
| GET | /trees | 定跡ツリー一覧 | 200 |
| GET | /trees/{tree_id} | 定跡ツリー詳細 | 200, 404 |
| PATCH | /trees/{tree_id} | 定跡ツリー更新 | 200, 404 |

### Nodes

| Method | Path | Description | Status Codes |
|--------|------|-------------|--------------|
| GET | /trees/{tree_id}/nodes/{node_id} | ノード詳細 | 200, 404 |
| DELETE | /trees/{tree_id}/nodes/{node_id} | ノード削除 | 204, 400, 404 |
| POST | /trees/{tree_id}/nodes/{node_id}/moves | 指し手追加 | 201, 400, 404, 409 |
| GET | /trees/{tree_id}/nodes/{node_id}/children | 子ノード一覧 | 200, 404 |

---

## リクエスト/レスポンス例

### POST /trees

**Request**:
```json
{
  "name": "矢倉",
  "description": "矢倉戦法の定跡集"
}
```

**Response 201**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "矢倉",
  "description": "矢倉戦法の定跡集",
  "node_count": 1,
  "created_at": "2026-01-16T12:00:00Z",
  "updated_at": "2026-01-16T12:00:00Z",
  "is_deleted": false,
  "deleted_at": null,
  "root_node": {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "tree_id": "550e8400-e29b-41d4-a716-446655440000",
    "sfen": "lnsgkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL b -",
    "ply": 0,
    "comment": "",
    "evaluation": null,
    "metadata": {},
    "is_root": true,
    "created_at": "2026-01-16T12:00:00Z",
    "updated_at": "2026-01-16T12:00:00Z"
  }
}
```

**Response 400**（名前が空）:
```json
{
  "error": "validation_error",
  "message": "名前は必須です",
  "details": {
    "name": ["この項目は必須です。"]
  }
}
```

---

### POST /trees/{tree_id}/nodes/{node_id}/moves

**Request**:
```json
{
  "move_usi": "7g7f"
}
```

**Response 201**（新規ノード作成）:
```json
{
  "edge": {
    "id": "550e8400-e29b-41d4-a716-446655440002",
    "move_usi": "7g7f",
    "move_japanese": ""
  },
  "child_node": {
    "id": "550e8400-e29b-41d4-a716-446655440003",
    "tree_id": "550e8400-e29b-41d4-a716-446655440000",
    "sfen": "lnsgkgsnl/1r5b1/ppppppppp/9/9/P/1PPPPPPPP/1B5R1/LNSGKGSNL w -",
    "ply": 1,
    "is_root": false,
    ...
  },
  "is_transposition": false
}
```

**Response 201**（転置検出）:
```json
{
  "edge": { ... },
  "child_node": {
    "id": "existing-node-id",
    ...
  },
  "is_transposition": true
}
```

**Response 400**（不正な指し手）:
```json
{
  "error": "invalid_format",
  "message": "指し手はUSI形式で入力してください（例: 7g7f, P*5e）",
  "move_usi": "invalid"
}
```

**Response 400**（合法でない指し手）:
```json
{
  "error": "illegal_move",
  "message": "合法でない指し手です: 9i9h",
  "move_usi": "9i9h"
}
```

**Response 409**（重複指し手）:
```json
{
  "error": "duplicate_move",
  "message": "指し手 7g7f は既に存在します"
}
```

---

### GET /trees/{tree_id}/nodes/{node_id}/children

**Response 200**:
```json
[
  {
    "node": {
      "id": "uuid",
      "sfen": "...",
      "ply": 1,
      ...
    },
    "move_usi": "7g7f",
    "move_japanese": "７六歩"
  },
  {
    "node": {
      "id": "uuid",
      "sfen": "...",
      "ply": 1,
      ...
    },
    "move_usi": "2g2f",
    "move_japanese": "２六歩"
  }
]
```

---

### DELETE /trees/{tree_id}/nodes/{node_id}

**Query Parameters**:
- `parent_id` (optional): 転置ノードの場合、削除するエッジの親ノードID

**Response 204**: 削除成功（ボディなし）

**Response 400**（ルートノード削除）:
```json
{
  "error": "cannot_delete_root",
  "message": "ルートノードは削除できません"
}
```

**Response 400**（転置ノードで parent_id 未指定）:
```json
{
  "error": "parent_id_required",
  "message": "転置ノードの削除には parent_id が必要です"
}
```

---

## エラーコード一覧

| error | HTTP Status | 説明 |
|-------|-------------|------|
| validation_error | 400 | バリデーションエラー |
| invalid_format | 400 | 指し手の形式が不正 |
| illegal_move | 400 | 合法でない指し手 |
| cannot_delete_root | 400 | ルートノード削除不可 |
| parent_id_required | 400 | 転置ノード削除に parent_id 必須 |
| not_found | 404 | リソースが見つからない |
| duplicate_move | 409 | 同じ指し手が既に存在 |

---

## 参照

- [openapi.yaml](../../002-joseki-manager/contracts/openapi.yaml) - 完全な API 定義
