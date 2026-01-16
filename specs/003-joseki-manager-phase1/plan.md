# Implementation Plan: Phase 1 Setup - プロジェクト初期化

**Branch**: `003-joseki-manager-phase1` | **Date**: 2026-01-14 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-joseki-manager-phase1/spec.md`

## Summary

Django プロジェクトの初期化と基本構造の構築。002-joseki-manager で設計されたアーキテクチャに基づき、uv を使用した依存関係管理でプロジェクトの骨格を構築する。このフェーズでは実際のビジネスロジックやデータモデルは実装せず、後続フェーズの開発基盤を整備する。

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: Django 5.0+, Django REST Framework 3.14+, cshogi 0.8+, drf-spectacular
**Storage**: PostgreSQL 15+
**Testing**: pytest, pytest-django, factory_boy
**Target Platform**: Linux/macOS/Windows（ローカルサーバー）
**Project Type**: Single project（REST APIバックエンド）
**Package Manager**: uv（requirements.txt は使用しない）
**Performance Goals**: N/A（セットアップフェーズ）
**Constraints**: シングルユーザー、認証なし、ローカル実行
**Scale/Scope**: プロジェクト初期化のみ

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| 原則 | 状態 | 対応 |
|------|------|------|
| I. 日本語ドキュメンテーション | ✅ Pass | すべての技術文書を日本語で作成 |
| II. シンプルさ優先 | ✅ Pass | 最小限のセットアップのみ実施、不要な設定は追加しない |
| III. 明確なコミュニケーション | ✅ Pass | quickstart.md で明確なセットアップ手順を提供 |
| IV. ブランチ運用ポリシー | ✅ Pass | `003-joseki-manager-phase1` ブランチで作業 |
| V. テスト駆動開発（TDD） | ✅ Pass | pytest 環境を整備、後続フェーズで TDD を実践可能に |

**判定**: すべてのゲートをパス。実装に進行可能。

## Project Structure

### Documentation (this feature)

```text
specs/003-joseki-manager-phase1/
├── plan.md              # This file
├── spec.md              # Feature specification
├── quickstart.md        # Development setup guide (uv 版)
└── checklists/
    └── requirements.md  # Quality checklist
```

### Source Code (repository root)

```text
src/
├── joseki/                    # Django プロジェクト
│   ├── __init__.py
│   ├── settings.py            # Django settings
│   ├── urls.py                # URL routing
│   └── wsgi.py
├── trees/                     # 定跡ツリー管理アプリ（空）
│   └── __init__.py
├── labels/                    # ラベル管理アプリ（空）
│   └── __init__.py
├── exports/                   # エクスポート機能アプリ（空）
│   └── __init__.py
├── core/                      # 共通機能（空）
│   └── __init__.py
└── manage.py

tests/
├── conftest.py                # pytest fixtures
├── factories.py               # factory_boy base setup
├── unit/
│   └── __init__.py
├── integration/
│   └── __init__.py
└── contract/
    └── __init__.py
```

**Structure Decision**: 002-joseki-manager の plan.md で定義された Single project 構造に従う。このフェーズでは空の Django アプリケーションディレクトリのみを作成し、後続フェーズでモデルとビューを追加する。

## Complexity Tracking

> **該当なし**: Constitution Check に違反がないため、複雑さの正当化は不要。

## Design Decisions

### 1. 依存関係管理ツール

**決定**: uv を使用（requirements.txt は使用しない）

**理由**:
- Issue #17 コメントでの明示的な要件
- 高速なパッケージ解決とインストール
- pyproject.toml で本番/開発依存を一元管理
- ロックファイルによる再現可能な環境

### 2. プロジェクト初期化アプローチ

**決定**: django-admin で直接プロジェクト構造を作成

**理由**:
- uv でパッケージをインストール後、django-admin コマンドで初期化
- カスタムテンプレートは使用せず、最小限の設定で開始
- 002-joseki-manager のドキュメントに従った構造

### 3. アプリケーション構成

**決定**: Phase 1 では空のアプリディレクトリのみ作成

**理由**:
- YAGNI の原則に従い、まずはディレクトリ構造のみ
- モデル・ビュー・シリアライザは後続フェーズで追加
- startapp コマンドは使用せず、手動でディレクトリを作成して柔軟性を確保

## Implementation Tasks

### Phase 1: プロジェクト初期化

| タスク | 説明 | 完了条件 |
|--------|------|----------|
| T001 | ディレクトリ構造の作成 | src/, tests/ 以下の構造が作成されている |
| T002 | pyproject.toml の作成（本番依存） | Django, DRF, cshogi 等が定義されている |
| T003 | pyproject.toml への開発依存追加 | pytest, black, ruff 等が dev group に定義されている |
| T004 | pyproject.toml のツール設定 | black, ruff, mypy, pytest の設定が含まれている |
| T005 | .env.example の作成 | DATABASE_URL, SECRET_KEY, DEBUG が定義されている |
| T006 | Django プロジェクト初期化 | src/joseki/ に Django 設定ファイルがある |
| T007 | settings.py の設定 | PostgreSQL, DRF, drf-spectacular が設定されている |
| T008 | urls.py の作成 | API バージョニング (/api/v1/) が設定されている |
| T009 | conftest.py の作成 | pytest-django の基本設定がある |
| T010 | factories.py の作成 | factory_boy の基本設定がある |

### 検証コマンド

```bash
# 依存関係のインストール
uv sync

# Django システムチェック
uv run python src/manage.py check

# テスト環境の確認
uv run pytest --collect-only
```

## Next Steps

1. `/speckit.tasks` で詳細なタスク一覧を生成
2. 各タスクを TDD サイクルで実装（可能な範囲で）
3. PR を `develop` ブランチに作成
4. マージ後、Phase 2（モデル実装）に進む

## Related Documents

- 親設計ブランチ: `002-joseki-manager`
- [spec.md](../002-joseki-manager/spec.md) - 機能仕様
- [plan.md](../002-joseki-manager/plan.md) - 実装計画
- [data-model.md](../002-joseki-manager/data-model.md) - データモデル設計
- [quickstart.md](./quickstart.md) - 開発環境セットアップ（uv 対応版）
