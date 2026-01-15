# Tasks: Phase 1 Setup - プロジェクト初期化

**Input**: 設計ドキュメント `/specs/002-joseki-manager/` より継承
**Prerequisites**: plan.md (002-joseki-manager), spec.md (002-joseki-manager)
**Related Issue**: #17

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 並列実行可能（異なるファイル、依存なし）
- **[Story]**: このタスクが属する User Story（例: US1, US2, US3）
- 各タスクに正確なファイルパスを含める

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- 依存関係管理: **uv** を使用（requirements.txt ではなく pyproject.toml）

---

## Phase 1: Setup (プロジェクト初期化)

**Purpose**: uv によるプロジェクト初期化と基本構造の構築

- [ ] T001 Create project directory structure per plan.md (`src/joseki/`, `src/trees/`, `src/labels/`, `src/exports/`, `src/core/`, `tests/`)
- [ ] T002 Initialize uv project with `uv init` and configure pyproject.toml

---

## Phase 2: User Story 1 - 開発環境のセットアップ (Priority: P1) 🎯 MVP

**Goal**: 開発者が `uv sync` で依存関係をインストールし、開発を開始できる

**Independent Test**: `uv sync` が成功し、依存関係がインストールされること

### Implementation for User Story 1

- [ ] T003 [US1] Add main dependencies to pyproject.toml (Django 5.0+, DRF 3.14+, django-filter, psycopg[binary], cshogi 0.8+, drf-spectacular) using `uv add`
- [ ] T004 [US1] Add dev dependencies to pyproject.toml (pytest 8.0+, pytest-django, pytest-cov, factory-boy, black, ruff, mypy, django-stubs, djangorestframework-stubs) using `uv add --dev`
- [ ] T005 [US1] Create `.env.example` with DATABASE_URL, SECRET_KEY, DEBUG, ALLOWED_HOSTS
- [ ] T006 [P] [US1] Configure tool settings in pyproject.toml (black, ruff, mypy, pytest)

**Checkpoint**: `uv sync` が成功し、依存関係がインストールされる

---

## Phase 3: User Story 2 - Django プロジェクト構造の構築 (Priority: P1)

**Goal**: `python manage.py check` が成功する Django プロジェクト

**Independent Test**: `uv run python manage.py check` が成功すること

### Implementation for User Story 2

- [ ] T007 [US2] Create `src/joseki/__init__.py`
- [ ] T008 [US2] Create `src/joseki/settings.py` with Django 5.0+ configuration (REST_FRAMEWORK, database, installed apps)
- [ ] T009 [US2] Create `src/joseki/urls.py` with API versioning (`/api/v1/`)
- [ ] T010 [US2] Create `src/joseki/wsgi.py`
- [ ] T011 [P] [US2] Create `src/manage.py` at src directory
- [ ] T012 [P] [US2] Create `src/trees/__init__.py`
- [ ] T013 [P] [US2] Create `src/labels/__init__.py`
- [ ] T014 [P] [US2] Create `src/exports/__init__.py`
- [ ] T015 [P] [US2] Create `src/core/__init__.py`

**Checkpoint**: `uv run python src/manage.py check` が成功する

---

## Phase 4: User Story 3 - テスト環境の準備 (Priority: P2)

**Goal**: pytest が実行可能な状態

**Independent Test**: `uv run pytest --collect-only` が成功すること

### Implementation for User Story 3

- [ ] T016 [US3] Create `tests/conftest.py` with pytest-django configuration
- [ ] T017 [US3] Create `tests/factories.py` with factory_boy base setup
- [ ] T018 [P] [US3] Create `tests/__init__.py`

**Checkpoint**: `uv run pytest --collect-only` が成功する

---

## Phase 5: Polish & ドキュメント更新

**Purpose**: 開発環境の完成度向上とドキュメント整備

- [ ] T019 Update `specs/003-joseki-manager-phase1/quickstart.md` with uv-based setup instructions
- [ ] T020 Validate all completion criteria from Issue #17

---

## Dependencies & Execution Order

### Phase Dependencies

- **Phase 1 (Setup)**: 依存なし - 即座に開始可能
- **Phase 2 (US1)**: Phase 1 完了後
- **Phase 3 (US2)**: Phase 2 完了後（依存関係が必要）
- **Phase 4 (US3)**: Phase 3 完了後（Django プロジェクトが必要）
- **Phase 5 (Polish)**: Phase 4 完了後

### User Story Dependencies

- **US1 (P1)**: Setup 完了後 - 他の Story に依存しない
- **US2 (P1)**: US1 完了後 - 依存関係がインストールされていることが必要
- **US3 (P2)**: US2 完了後 - Django プロジェクトが必要

### Parallel Opportunities

- T006: ツール設定は依存関係追加と並列可能
- T011-T015: Django アプリの `__init__.py` は並列作成可能
- T018: `tests/__init__.py` は conftest.py と並列作成可能

---

## Parallel Example: User Story 2

```bash
# Django アプリの __init__.py を並列作成:
Task: "Create src/trees/__init__.py"
Task: "Create src/labels/__init__.py"
Task: "Create src/exports/__init__.py"
Task: "Create src/core/__init__.py"
```

---

## Implementation Strategy

### MVP First (Phase 1-3)

1. Phase 1: Setup 完了
2. Phase 2: US1（開発環境）完了 → `uv sync` 検証
3. Phase 3: US2（Django 構造）完了 → `manage.py check` 検証
4. **STOP and VALIDATE**: Issue #17 の主要完了条件を達成

### Completion Criteria (Issue #17)

- [ ] すべてのディレクトリ構造が作成されている
- [ ] `uv sync` が成功する（requirements.txt → uv に変更）
- [ ] `uv run python src/manage.py check` が成功する
- [ ] `uv run pytest --collect-only` が実行可能
- [ ] PR が `develop` にマージされている

---

## Notes

- [P] タスク = 異なるファイル、依存なし
- [Story] ラベルは特定の User Story へのトレーサビリティを確保
- 各 User Story は独立して完了・テスト可能
- コミットは各タスクまたは論理的なグループ単位で実施
- **uv** を使用: `pip install` → `uv sync` / `uv add`

---

## Summary

| 項目 | 値 |
|------|------|
| 合計タスク数 | 20 |
| Setup タスク | 2 |
| US1 タスク | 4 |
| US2 タスク | 9 |
| US3 タスク | 3 |
| Polish タスク | 2 |
| 並列実行可能 | 7 tasks (T006, T011-T015, T018) |

**MVP スコープ**: Phase 1-3（T001-T015）で Issue #17 の主要完了条件を達成
