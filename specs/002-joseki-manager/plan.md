# Implementation Plan: 将棋定跡管理アプリケーション（Joseki Manager）

**Branch**: `002-joseki-manager` | **Date**: 2026-01-12 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-joseki-manager/spec.md`

## Summary

将棋の序盤定跡を木構造（DAG）形式で管理するREST APIバックエンド。Python + Django REST Framework + PostgreSQL で構築し、cshogi ライブラリを使用して将棋のルール検証・棋譜解析を行う。初期リリースはシングルユーザー・ローカル実行前提のAPIのみを提供。

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: Django 5.0+, Django REST Framework 3.14+, cshogi 0.8+
**Storage**: PostgreSQL 15+
**Testing**: pytest, pytest-django, factory_boy
**Target Platform**: Linux/macOS/Windows（ローカルサーバー）
**Project Type**: Single project（REST APIバックエンド）
**Performance Goals**: API応答 1秒以内（100ノード）、2秒以内（1000ノード検索）
**Constraints**: シングルユーザー、認証なし、ローカル実行
**Scale/Scope**: 定跡ツリー数十個、ノード数千〜数万規模

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| 原則 | 状態 | 対応 |
|------|------|------|
| I. 日本語ドキュメンテーション | ✅ Pass | すべての技術文書を日本語で作成 |
| II. シンプルさ優先 | ✅ Pass | 隣接リスト+エッジテーブルによるシンプルなモデル設計 |
| III. 明確なコミュニケーション | ✅ Pass | OpenAPI仕様による明確なAPI定義 |
| IV. ブランチ運用ポリシー | ✅ Pass | `002-joseki-manager` ブランチで作業中 |
| V. テスト駆動開発（TDD） | ✅ Pass | Red-Green-Refactorサイクルを徹底 |

**判定**: すべてのゲートをパス。Phase 0に進行可能。

## Project Structure

### Documentation (this feature)

```text
specs/002-joseki-manager/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0: Technical research
├── data-model.md        # Phase 1: Entity definitions
├── quickstart.md        # Phase 1: Development setup guide
├── contracts/           # Phase 1: API contracts
│   └── openapi.yaml     # OpenAPI 3.0 specification
├── checklists/          # Quality checklists
│   └── requirements.md  # Specification checklist
└── tasks.md             # Phase 2: Implementation tasks
```

### Source Code (repository root)

```text
src/
├── joseki/                    # Django project
│   ├── __init__.py
│   ├── settings.py            # Django settings
│   ├── urls.py                # URL routing
│   └── wsgi.py
├── trees/                     # 定跡ツリー管理アプリ
│   ├── __init__.py
│   ├── models.py              # JosekiTree, Node, Edge models
│   ├── serializers.py         # DRF serializers
│   ├── views.py               # API views
│   ├── urls.py                # App URLs
│   └── services/              # Business logic
│       ├── __init__.py
│       ├── move_validator.py  # cshogi integration
│       └── kif_parser.py      # KIF/KI2 import
├── labels/                    # ラベル管理アプリ
│   ├── __init__.py
│   ├── models.py              # Label, NodeLabel models
│   ├── serializers.py
│   ├── views.py
│   └── urls.py
├── exports/                   # エクスポート機能アプリ
│   ├── __init__.py
│   ├── views.py
│   └── services/
│       ├── __init__.py
│       ├── json_exporter.py
│       └── kif_exporter.py
└── core/                      # 共通機能
    ├── __init__.py
    └── shogi/                 # 将棋ロジックラッパー
        ├── __init__.py
        ├── position.py        # SFEN handling
        └── rules.py           # Move validation

tests/
├── conftest.py                # pytest fixtures
├── factories.py               # factory_boy factories
├── unit/
│   ├── test_models.py
│   ├── test_move_validator.py
│   └── test_kif_parser.py
├── integration/
│   └── test_api.py
└── contract/
    └── test_openapi.py        # Contract tests
```

**Structure Decision**: Single project構造を採用。REST APIのみの初期リリースのため、バックエンド単体で完結。将来のフロントエンド追加時はmonorepo化を検討。

## Complexity Tracking

> **該当なし**: Constitution Checkに違反がないため、複雑さの正当化は不要。

## Design Decisions

### 1. データモデル設計

**決定**: 隣接リスト + エッジテーブル（DAG構造）

**理由**:
- 転置（同一局面への複数経路）をサポートするため純粋な木構造ではなくDAGが必要
- django-mptt/treebeardは純粋な木構造向けで、転置に対応できない
- シンプルな隣接リストで十分な性能が得られる（1000ノード規模）

### 2. 将棋ライブラリ

**決定**: cshogi

**理由**:
- Cython実装で高速
- KIF/KI2パーサー内蔵
- 合法手検証（二歩・打ち歩詰め自動除外）
- SFEN完全サポート
- アクティブにメンテナンスされている

### 3. 局面の一意性

**決定**: SFEN文字列をキーとして使用

**理由**:
- 将棋界で標準的な局面表現形式
- cshogi/python-shogiで直接サポート
- 文字列比較で転置検出が容易

## Next Steps

1. `research.md` - 技術調査結果の詳細（完了）
2. `data-model.md` - エンティティ定義とリレーション
3. `contracts/openapi.yaml` - API仕様
4. `quickstart.md` - 開発環境セットアップ
5. `/speckit.tasks` - 実装タスク生成
