# Tasks: Phase 1 Setup - プロジェクト初期化

**Input**: Design documents from `/specs/003-joseki-manager-phase1/` and `/specs/002-joseki-manager/`
**Prerequisites**: spec.md (required), plan.md from 002-joseki-manager (required)

**Tests**: テストタスクは含まない（このフェーズはインフラセットアップのため）

**Organization**: User Story ごとにタスクを整理し、独立した実装とテストを可能にする

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 並列実行可能（異なるファイル、依存関係なし）
- **[Story]**: 所属する User Story（US1, US2, US3）
- 説明には正確なファイルパスを含む

---

## Phase 1: Setup（共有インフラストラクチャ）

**Purpose**: プロジェクト初期化と基本構造

- [ ] T001 Create project directory structure per plan.md (src/joseki/, src/trees/, src/labels/, src/exports/, src/core/, tests/)
- [ ] T002 Create pyproject.toml with project metadata and Python version requirement (>=3.11)

---

## Phase 2: User Story 1 - 開発環境のセットアップ (Priority: P1) 🎯 MVP

**Goal**: `uv sync` コマンドで必要なすべての依存関係がインストールされ、開発を開始できる状態になる

**Independent Test**: `uv sync` → `uv run python src/manage.py check` がエラーなく完了

### Implementation for User Story 1

- [ ] T003 [US1] Add production dependencies to pyproject.toml (Django 5.0+, djangorestframework 3.14+, cshogi 0.8+, psycopg[binary], drf-spectacular, django-filter)
- [ ] T004 [US1] Add development dependencies to pyproject.toml (pytest, pytest-django, pytest-cov, factory-boy, black, ruff, mypy, django-stubs, djangorestframework-stubs)
- [ ] T005 [US1] Configure tool settings in pyproject.toml ([tool.black], [tool.ruff], [tool.mypy], [tool.pytest.ini_options])
- [ ] T006 [P] [US1] Create .env.example with DATABASE_URL, SECRET_KEY, DEBUG, ALLOWED_HOSTS

**Checkpoint**: `uv sync` が成功し、依存関係がインストールされる

---

## Phase 3: User Story 2 - Django プロジェクト構造の構築 (Priority: P1)

**Goal**: plan.md で定義されたディレクトリ構造に従って Django プロジェクトとアプリケーションを作成

**Independent Test**: `uv run python src/manage.py check` がエラーなく完了

### Implementation for User Story 2

- [ ] T007 [US2] Initialize Django project in src/joseki/ (settings.py, urls.py, wsgi.py, asgi.py, __init__.py)
- [ ] T008 [US2] Create src/manage.py pointing to joseki.settings
- [ ] T009 [US2] Configure src/joseki/settings.py (PostgreSQL, DRF, drf-spectacular, INSTALLED_APPS)
- [ ] T010 [US2] Create src/joseki/urls.py with API versioning (/api/v1/)
- [ ] T011 [P] [US2] Create src/trees/__init__.py (Django app placeholder)
- [ ] T012 [P] [US2] Create src/labels/__init__.py (Django app placeholder)
- [ ] T013 [P] [US2] Create src/exports/__init__.py (Django app placeholder)
- [ ] T014 [P] [US2] Create src/core/__init__.py (shared utilities placeholder)

**Checkpoint**: `uv run python src/manage.py check` が成功

---

## Phase 4: User Story 3 - テスト環境の準備 (Priority: P2)

**Goal**: pytest と pytest-django を使用してテストを実行できる環境を構築

**Independent Test**: `uv run pytest --collect-only` がエラーなく完了

### Implementation for User Story 3

- [ ] T015 [US3] Create tests/__init__.py
- [ ] T016 [US3] Create tests/conftest.py with pytest-django configuration (django_db_setup, pytest.ini settings)
- [ ] T017 [US3] Create tests/factories.py with factory_boy base setup (BaseFactory)

**Checkpoint**: `uv run pytest --collect-only` が成功

---

## Phase 5: Polish & クロスカット関心事

**Purpose**: 複数の User Story に影響する改善

- [ ] T018 Update specs/002-joseki-manager/quickstart.md for uv-based setup (if needed)
- [ ] T019 Validate all success criteria from spec.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: 依存なし - すぐに開始可能
- **User Story 1 (Phase 2)**: Setup 完了後に開始
- **User Story 2 (Phase 3)**: User Story 1 完了後に開始（依存関係がインストールされている必要あり）
- **User Story 3 (Phase 4)**: User Story 2 完了後に開始（Django プロジェクト構造が必要）
- **Polish (Phase 5)**: すべての User Story 完了後

### Within Each Phase

- [P] マークのタスクは並列実行可能
- 並列マークなしのタスクは順次実行

### Parallel Opportunities

```bash
# Phase 1: すべて順次（依存関係あり）
Task T001 → Task T002

# Phase 2: T003-T005 は順次（同じファイル）、T006 は並列可能
Task T003 → T004 → T005
Task T006  # 並列実行可能

# Phase 3: T007-T010 は順次、T011-T014 は並列可能
Task T007 → T008 → T009 → T010
Task T011, T012, T013, T014  # 並列実行可能

# Phase 4: すべて順次
Task T015 → T016 → T017
```

---

## Implementation Strategy

### MVP First (User Story 1 + 2)

1. Phase 1 完了: Setup
2. Phase 2 完了: User Story 1（依存関係インストール）
3. Phase 3 完了: User Story 2（Django 構造）
4. **STOP and VALIDATE**: `uv sync` + `uv run python src/manage.py check` が成功
5. Issue #17 の完了条件を満たす

### Incremental Delivery

1. Setup + US1 → 依存関係がインストール可能
2. + US2 → Django プロジェクトが動作
3. + US3 → テスト環境が準備完了
4. 各ステップで価値を追加、前のステップを壊さない

---

## Summary

| Metric | Value |
|--------|-------|
| Total Tasks | 19 |
| Setup Tasks | 2 |
| US1 Tasks | 4 |
| US2 Tasks | 8 |
| US3 Tasks | 3 |
| Polish Tasks | 2 |
| Parallel Opportunities | 6 tasks (T006, T011-T014) |

**MVP Scope**: Phase 1-3（T001-T014）で Issue #17 の主要完了条件を達成

---

## Notes

- [P] タスク = 異なるファイル、依存関係なし
- [Story] ラベルは特定の User Story への追跡可能性を提供
- 各 User Story は独立して完了・テスト可能
- タスクまたは論理グループごとにコミット
- どのチェックポイントでも停止して Story を独立して検証可能
