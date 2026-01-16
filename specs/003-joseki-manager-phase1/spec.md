# Feature Specification: Phase 1 Setup - プロジェクト初期化

**Feature Branch**: `003-joseki-manager-phase1`
**Created**: 2026-01-14
**Status**: Draft
**Input**: Issue #17 - Django プロジェクトの初期化と基本構造の構築。uv を使用した依存関係管理。

## 概要

将棋定跡管理アプリケーション（Joseki Manager）の Django プロジェクト初期化。
設計ドキュメント（002-joseki-manager）に基づき、プロジェクト構造を構築する。
依存関係管理には uv を使用する。

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 開発環境のセットアップ (Priority: P1)

開発者はリポジトリをクローンした後、`uv sync` コマンドを実行するだけで、必要なすべての依存関係がインストールされ、開発を開始できる状態になる。

**Why this priority**: 他のすべての開発作業の前提条件。環境構築ができなければ何も始まらない。

**Independent Test**: `uv sync` を実行し、Django プロジェクトが正常に動作することを確認。

**Acceptance Scenarios**:

1. **Given** リポジトリをクローンした状態、**When** `uv sync` を実行、**Then** 必要なすべてのパッケージがインストールされる
2. **Given** パッケージがインストールされた状態、**When** `uv run python src/manage.py check` を実行、**Then** システムチェックがエラーなく完了する
3. **Given** パッケージがインストールされた状態、**When** `uv run pytest` を実行、**Then** pytest が正常に起動する

---

### User Story 2 - Django プロジェクト構造の構築 (Priority: P1)

開発者は plan.md で定義されたディレクトリ構造に従って Django プロジェクトとアプリケーションを作成できる。これにより、後続の Phase でモデルやビューを追加する基盤が整う。

**Why this priority**: コードを書く場所がなければ開発を進められない。

**Independent Test**: 定義されたディレクトリ構造が存在し、Django アプリケーションとして認識されることを確認。

**Acceptance Scenarios**:

1. **Given** セットアップが完了した状態、**When** `src/` ディレクトリを確認、**Then** joseki, trees, labels, exports, core のディレクトリが存在する
2. **Given** Django プロジェクトが初期化された状態、**When** settings.py を確認、**Then** PostgreSQL, DRF, drf-spectacular が設定されている
3. **Given** プロジェクト構造が作成された状態、**When** `uv run python src/manage.py runserver --check` を実行、**Then** サーバーが起動可能な状態である

---

### User Story 3 - テスト環境の準備 (Priority: P2)

開発者は pytest と pytest-django を使用してテストを実行できる。conftest.py と factory_boy の基本設定が整っており、TDD で開発を進められる。

**Why this priority**: TDD を実践するためにはテスト環境が必要。ただし、基本構造より優先度は低い。

**Independent Test**: `uv run pytest --collect-only` でテスト収集が動作することを確認。

**Acceptance Scenarios**:

1. **Given** テスト環境が設定された状態、**When** `uv run pytest --collect-only` を実行、**Then** テストファイルが収集される
2. **Given** conftest.py が存在する状態、**When** pytest-django の設定を確認、**Then** Django テスト用の fixture が利用可能

---

### Edge Cases

- Python 3.11 未満の環境でセットアップを試みた場合は？→ pyproject.toml で Python >= 3.11 を指定し、uv がエラーを表示
- PostgreSQL がインストールされていない環境では？→ .env.example にセットアップ手順を記載。初回実行時のエラーメッセージで案内
- 既存の仮想環境がある場合は？→ uv は独自の仮想環境を .venv に作成するため競合しない

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: プロジェクトは uv を使用して依存関係を管理する（requirements.txt は使用しない）
- **FR-002**: pyproject.toml に本番用と開発用の依存関係を定義する
- **FR-003**: Django 5.0+, DRF 3.14+, cshogi 0.8+ を依存関係として含む
- **FR-004**: pytest, pytest-django, factory-boy, black, ruff, mypy を開発用依存関係として含む
- **FR-005**: plan.md で定義されたディレクトリ構造（src/joseki/, src/trees/, src/labels/, src/exports/, src/core/, tests/）を作成する
- **FR-006**: Django プロジェクトを src/joseki/ に初期化する
- **FR-007**: settings.py で PostgreSQL, DRF, drf-spectacular を設定する
- **FR-008**: API バージョニング（/api/v1/）を含む urls.py を作成する
- **FR-009**: tests/conftest.py に pytest-django の設定を作成する
- **FR-010**: tests/factories.py に factory_boy の基本設定を作成する
- **FR-011**: .env.example に必要な環境変数（DATABASE_URL, SECRET_KEY, DEBUG, ALLOWED_HOSTS）を定義する

### Key Entities

このフェーズではデータモデルは作成しない。ディレクトリ構造と設定ファイルのみ。

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: `uv sync` コマンドが成功する
- **SC-002**: `uv run python src/manage.py check` がエラーなく完了する
- **SC-003**: `uv run pytest --collect-only` がエラーなく完了する
- **SC-004**: plan.md で定義されたすべてのディレクトリが存在する
- **SC-005**: pyproject.toml に必要なすべての依存関係が定義されている

## Assumptions

- 開発者は uv をインストール済みである（グローバルインストール）
- PostgreSQL 15+ がローカルにインストールされている
- Python 3.11+ が利用可能である
- 002-joseki-manager の plan.md と quickstart.md の設計に従う

## Related Documents

- 設計ブランチ: `002-joseki-manager`
- [spec.md](../002-joseki-manager/spec.md) - 機能仕様
- [plan.md](../002-joseki-manager/plan.md) - 実装計画
- [tasks.md](../002-joseki-manager/tasks.md) - タスク一覧
- [quickstart.md](../002-joseki-manager/quickstart.md) - 開発環境セットアップ（uv 対応版に更新予定）

## タスク一覧（Issue #17 より、uv 対応版）

- [ ] T001 Create project directory structure per plan.md
- [ ] T002 Create pyproject.toml with dependencies (Django 5.0+, DRF 3.14+, cshogi 0.8+, psycopg, drf-spectacular, django-filter)
- [ ] T003 Add dev dependencies to pyproject.toml (pytest, pytest-django, factory-boy, black, ruff, mypy)
- [ ] T004 Configure tool settings in pyproject.toml (black, ruff, mypy, pytest)
- [ ] T005 Create .env.example with DATABASE_URL, SECRET_KEY, DEBUG, ALLOWED_HOSTS
- [ ] T006 Initialize Django project in src/joseki/
- [ ] T007 Configure src/joseki/settings.py
- [ ] T008 Create src/joseki/urls.py with API versioning
- [ ] T009 Create tests/conftest.py with pytest-django configuration
- [ ] T010 Create tests/factories.py with factory_boy base setup
