# Tasks: 将棋定跡管理アプリケーション（Joseki Manager）

**Input**: Design documents from `/specs/002-joseki-manager/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/openapi.yaml, quickstart.md

**Tests**: Constitution V (TDD) に従い、すべての実装タスクにテストタスクを含む。Red-Green-Refactor サイクルを徹底。

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Django project: `src/joseki/` (settings), `src/trees/`, `src/labels/`, `src/exports/`, `src/core/`
- Tests: `tests/unit/`, `tests/integration/`, `tests/contract/`

---

## Phase 1: Setup (Project Initialization)

**Purpose**: Django プロジェクトの初期化と基本構造の構築

- [ ] T001 Create project directory structure per plan.md (`src/joseki/`, `src/trees/`, `src/labels/`, `src/exports/`, `src/core/`, `tests/`)
- [ ] T002 Create requirements.txt with Django 5.0+, DRF 3.14+, cshogi 0.8+, psycopg, drf-spectacular
- [ ] T003 [P] Create requirements-dev.txt with pytest, pytest-django, factory-boy, black, ruff, mypy
- [ ] T004 [P] Create pyproject.toml with tool configurations (black, ruff, mypy, pytest)
- [ ] T005 Create .env.example with DATABASE_URL, SECRET_KEY, DEBUG, ALLOWED_HOSTS
- [ ] T006 Initialize Django project in src/joseki/ (`django-admin startproject joseki src`)
- [ ] T007 Configure src/joseki/settings.py with PostgreSQL, DRF, drf-spectacular, installed apps
- [ ] T008 [P] Create src/joseki/urls.py with API versioning (`/api/v1/`)
- [ ] T009 [P] Create tests/conftest.py with pytest-django configuration
- [ ] T010 [P] Create tests/factories.py with factory_boy base setup

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: 全ユーザーストーリーが依存するコアインフラの構築

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Core Infrastructure

- [ ] T011 Create Django app `trees` (`python manage.py startapp trees src/trees`)
- [ ] T012 Create Django app `labels` (`python manage.py startapp labels src/labels`)
- [ ] T013 Create Django app `exports` (`python manage.py startapp exports src/exports`)
- [ ] T014 Create Django app `core` (`python manage.py startapp core src/core`)
- [ ] T015 Create src/core/shogi/__init__.py, src/core/shogi/position.py, src/core/shogi/rules.py

### Base Models (Tests First - TDD)

- [ ] T016 [P] Write failing test for JosekiTree model in tests/unit/test_models.py
- [ ] T017 [P] Write failing test for Node model in tests/unit/test_models.py
- [ ] T018 [P] Write failing test for Edge model in tests/unit/test_models.py
- [ ] T019 [P] Write failing test for Label model in tests/unit/test_models.py
- [ ] T020 [P] Write failing test for NodeLabel model in tests/unit/test_models.py
- [ ] T021 Implement JosekiTree model in src/trees/models.py (make T016 pass)
- [ ] T022 Implement Node model in src/trees/models.py (make T017 pass)
- [ ] T023 Implement Edge model in src/trees/models.py (make T018 pass)
- [ ] T024 Implement Label model in src/labels/models.py (make T019 pass)
- [ ] T025 Implement NodeLabel model in src/labels/models.py (make T020 pass)
- [ ] T026 Create initial migrations (`python manage.py makemigrations trees labels`)
- [ ] T027 Apply migrations (`python manage.py migrate`)

### cshogi Integration (Tests First - TDD)

- [ ] T028 Write failing test for SFEN handling in tests/unit/test_position.py
- [ ] T029 Write failing test for move validation in tests/unit/test_move_validator.py
- [ ] T030 Implement SFEN utilities in src/core/shogi/position.py (make T028 pass)
- [ ] T031 Implement move validator using cshogi in src/trees/services/move_validator.py (make T029 pass)

### Factory Setup

- [ ] T032 [P] Create JosekiTreeFactory in tests/factories.py
- [ ] T033 [P] Create NodeFactory in tests/factories.py
- [ ] T034 [P] Create EdgeFactory in tests/factories.py
- [ ] T035 [P] Create LabelFactory in tests/factories.py

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - 定跡ツリーの作成と手順入力 (Priority: P1) MVP

**Goal**: ユーザーは定跡ツリーを作成し、初期局面から分岐する手順を木構造形式で入力できる

**Independent Test**: 定跡ツリーを新規作成し、初手から5手程度の分岐を含む手順を入力、保存、再読み込みできることを確認

**Related FRs**: FR-001, FR-002, FR-003, FR-004, FR-007, FR-008, FR-012, FR-013

### Contract Tests for User Story 1 (TDD - Red)

- [ ] T036 [P] [US1] Contract test for POST /trees in tests/contract/test_trees_api.py
- [ ] T037 [P] [US1] Contract test for GET /trees/{id} in tests/contract/test_trees_api.py
- [ ] T038 [P] [US1] Contract test for GET /trees in tests/contract/test_trees_api.py
- [ ] T039 [P] [US1] Contract test for PATCH /trees/{id} in tests/contract/test_trees_api.py
- [ ] T040 [P] [US1] Contract test for POST /nodes/{id}/moves in tests/contract/test_nodes_api.py
- [ ] T041 [P] [US1] Contract test for GET /nodes/{id}/children in tests/contract/test_nodes_api.py
- [ ] T041b [P] [US1] Contract test for DELETE /nodes/{id} in tests/contract/test_nodes_api.py

### Integration Tests for User Story 1 (TDD - Red)

- [ ] T042 [P] [US1] Integration test for tree creation with root node in tests/integration/test_tree_workflow.py
- [ ] T043 [P] [US1] Integration test for adding moves and creating branches in tests/integration/test_tree_workflow.py
- [ ] T044 [P] [US1] Integration test for transposition detection in tests/integration/test_tree_workflow.py
- [ ] T045 [P] [US1] Integration test for illegal move rejection in tests/integration/test_tree_workflow.py
- [ ] T045b [P] [US1] Integration test for deleting edge from transposition node (node with multiple parents) in tests/integration/test_tree_workflow.py

### Implementation for User Story 1 (TDD - Green)

- [ ] T046 [P] [US1] Create JosekiTreeSerializer in src/trees/serializers.py
- [ ] T047 [P] [US1] Create NodeSerializer in src/trees/serializers.py
- [ ] T048 [P] [US1] Create EdgeSerializer in src/trees/serializers.py
- [ ] T049 [P] [US1] Create MoveCreateSerializer in src/trees/serializers.py
- [ ] T050 [US1] Implement TreeService in src/trees/services/tree_service.py (tree CRUD, root node auto-creation)
- [ ] T051 [US1] Implement NodeService in src/trees/services/node_service.py (add move, transposition detection)
- [ ] T052 [US1] Implement JosekiTreeViewSet in src/trees/views.py (list, create, retrieve, update)
- [ ] T053 [US1] Implement NodeViewSet in src/trees/views.py (retrieve, children, add_move)
- [ ] T054 [US1] Configure URL routing in src/trees/urls.py
- [ ] T055 [US1] Register trees URLs in src/joseki/urls.py
- [ ] T056 [US1] Verify all US1 contract tests pass
- [ ] T057 [US1] Verify all US1 integration tests pass

**Checkpoint**: User Story 1 complete - 定跡ツリーの作成と手順入力が機能する

---

## Phase 4: User Story 2 - 戦型ラベルの付与と管理 (Priority: P1)

**Goal**: ユーザーは任意の局面にラベルを付与し、ラベルで検索・フィルタリングできる

**Independent Test**: 任意の局面にラベルを付与し、そのラベルで検索・フィルタリングできることを確認

**Related FRs**: FR-005, FR-006

### Contract Tests for User Story 2 (TDD - Red)

- [ ] T058 [P] [US2] Contract test for GET /labels in tests/contract/test_labels_api.py
- [ ] T059 [P] [US2] Contract test for POST /labels in tests/contract/test_labels_api.py
- [ ] T060 [P] [US2] Contract test for PATCH /labels/{id} in tests/contract/test_labels_api.py
- [ ] T061 [P] [US2] Contract test for DELETE /labels/{id} in tests/contract/test_labels_api.py
- [ ] T062 [P] [US2] Contract test for POST /nodes/{id}/labels in tests/contract/test_labels_api.py
- [ ] T063 [P] [US2] Contract test for DELETE /nodes/{id}/labels/{label_id} in tests/contract/test_labels_api.py
- [ ] T064 [P] [US2] Contract test for GET /search/nodes?label_id= in tests/contract/test_search_api.py

### Integration Tests for User Story 2 (TDD - Red)

- [ ] T065 [P] [US2] Integration test for label CRUD workflow in tests/integration/test_label_workflow.py
- [ ] T066 [P] [US2] Integration test for node label assignment in tests/integration/test_label_workflow.py
- [ ] T067 [P] [US2] Integration test for label search across trees in tests/integration/test_label_workflow.py
- [ ] T067b [P] [US2] Integration test for label with special characters (emoji, Japanese, symbols) in tests/integration/test_label_workflow.py

### Implementation for User Story 2 (TDD - Green)

- [ ] T068 [P] [US2] Create LabelSerializer in src/labels/serializers.py
- [ ] T069 [P] [US2] Create NodeLabelSerializer in src/labels/serializers.py
- [ ] T070 [US2] Implement LabelService in src/labels/services/label_service.py
- [ ] T071 [US2] Implement LabelViewSet in src/labels/views.py
- [ ] T072 [US2] Implement NodeLabelView in src/labels/views.py (add/remove labels)
- [ ] T073 [US2] Implement SearchViewSet in src/trees/views.py (search/nodes endpoint)
- [ ] T074 [US2] Configure URL routing in src/labels/urls.py
- [ ] T075 [US2] Register labels URLs in src/joseki/urls.py
- [ ] T076 [US2] Verify all US2 contract tests pass
- [ ] T077 [US2] Verify all US2 integration tests pass

**Checkpoint**: User Story 2 complete - ラベル付与と検索が機能する

---

## Phase 5: User Story 3 - 定跡ツリーの視覚的表示と操作 (Priority: P2)

**Goal**: APIは定跡ツリーを木構造形式で表現するデータ構造を提供する（視覚的描画はクライアント側責務）

**Independent Test**: 50手以上の分岐を持つ定跡ツリーを深さ制限付きで取得できることを確認

**Related FRs**: FR-007, FR-008 (データ構造提供、描画はクライアント側)

### Contract Tests for User Story 3 (TDD - Red)

- [ ] T078 [P] [US3] Contract test for GET /trees/{id}?depth= in tests/contract/test_trees_api.py
- [ ] T079 [P] [US3] Contract test for GET /nodes/{id} with parent info in tests/contract/test_nodes_api.py

### Integration Tests for User Story 3 (TDD - Red)

- [ ] T080 [P] [US3] Integration test for depth-limited tree retrieval in tests/integration/test_tree_display.py
- [ ] T081 [P] [US3] Integration test for large tree (100+ nodes) performance in tests/integration/test_tree_display.py

### Implementation for User Story 3 (TDD - Green)

- [ ] T082 [US3] Enhance NodeSerializer with parent edges info in src/trees/serializers.py
- [ ] T083 [US3] Implement depth-limited tree serialization in src/trees/serializers.py
- [ ] T084 [US3] Add depth parameter handling in JosekiTreeViewSet.retrieve in src/trees/views.py
- [ ] T085 [US3] Verify all US3 contract tests pass
- [ ] T086 [US3] Verify all US3 integration tests pass

**Checkpoint**: User Story 3 complete - 深さ制限付きツリーデータ取得が機能する

---

## Phase 6: User Story 4 - 定跡データのインポート・エクスポート (Priority: P2)

**Goal**: ユーザーはKIF/KI2形式の棋譜をインポートし、JSON/KIF形式でエクスポートできる

**Independent Test**: KIF形式の棋譜ファイルをインポートし、その手順が定跡ツリーとして反映されることを確認

**Related FRs**: FR-009, FR-010, FR-014, FR-015

### Unit Tests for KIF Parser (TDD - Red)

- [ ] T087 [P] [US4] Write failing test for KIF file parsing in tests/unit/test_kif_parser.py
- [ ] T088 [P] [US4] Write failing test for KI2 file parsing in tests/unit/test_kif_parser.py
- [ ] T089 [P] [US4] Write failing test for JSON export in tests/unit/test_exporter.py
- [ ] T090 [P] [US4] Write failing test for KIF export in tests/unit/test_exporter.py

### Contract Tests for User Story 4 (TDD - Red)

- [ ] T091 [P] [US4] Contract test for POST /trees/{id}/import in tests/contract/test_import_api.py
- [ ] T092 [P] [US4] Contract test for GET /trees/{id}/export?format=json in tests/contract/test_export_api.py
- [ ] T093 [P] [US4] Contract test for GET /trees/{id}/export?format=kif in tests/contract/test_export_api.py
- [ ] T094 [P] [US4] Contract test for POST /trees/{id}/merge in tests/contract/test_merge_api.py

### Integration Tests for User Story 4 (TDD - Red)

- [ ] T095 [P] [US4] Integration test for KIF import workflow in tests/integration/test_import_export.py
- [ ] T096 [P] [US4] Integration test for merge with conflict resolution in tests/integration/test_import_export.py
- [ ] T097 [P] [US4] Integration test for round-trip (export then import) in tests/integration/test_import_export.py

### Implementation for User Story 4 (TDD - Green)

- [ ] T098 [US4] Implement KIF/KI2 parser in src/trees/services/kif_parser.py (make T087, T088 pass)
- [ ] T099 [US4] Implement JSON exporter in src/exports/services/json_exporter.py (make T089 pass)
- [ ] T100 [US4] Implement KIF exporter in src/exports/services/kif_exporter.py (make T090 pass)
- [ ] T101 [US4] Implement ImportService in src/trees/services/import_service.py
- [ ] T102 [US4] Implement MergeService in src/trees/services/merge_service.py
- [ ] T103 [US4] Implement ImportView in src/trees/views.py
- [ ] T104 [US4] Implement ExportView in src/exports/views.py
- [ ] T105 [US4] Implement MergeView in src/trees/views.py
- [ ] T106 [US4] Configure URL routing in src/exports/urls.py
- [ ] T107 [US4] Register exports URLs in src/joseki/urls.py
- [ ] T108 [US4] Verify all US4 contract tests pass
- [ ] T109 [US4] Verify all US4 integration tests pass

**Checkpoint**: User Story 4 complete - インポート・エクスポート・マージが機能する

---

## Phase 7: User Story 5 - コメント・メモの追加 (Priority: P3)

**Goal**: ユーザーは任意のノードにコメントを追加できる

**Independent Test**: 任意のノードにコメントを追加し、後から確認・編集できることを確認

**Related FRs**: FR-011

### Contract Tests for User Story 5 (TDD - Red)

- [ ] T110 [P] [US5] Contract test for PATCH /nodes/{id} with comment in tests/contract/test_nodes_api.py
- [ ] T111 [P] [US5] Contract test for GET /nodes/{id} returning comment in tests/contract/test_nodes_api.py

### Integration Tests for User Story 5 (TDD - Red)

- [ ] T112 [P] [US5] Integration test for comment CRUD workflow in tests/integration/test_comment_workflow.py

### Implementation for User Story 5 (TDD - Green)

- [ ] T113 [US5] Add comment update to NodeSerializer in src/trees/serializers.py
- [ ] T114 [US5] Add comment update to NodeViewSet.partial_update in src/trees/views.py
- [ ] T115 [US5] Verify all US5 contract tests pass
- [ ] T116 [US5] Verify all US5 integration tests pass

**Checkpoint**: User Story 5 complete - コメント機能が機能する

---

## Phase 8: Trash & Recovery (Cross-Cutting)

**Goal**: 定跡ツリーのゴミ箱機能と復元機能を実装する

**Related FRs**: FR-016, FR-017

### Contract Tests for Trash (TDD - Red)

- [ ] T117 [P] Contract test for DELETE /trees/{id} (soft delete) in tests/contract/test_trees_api.py
- [ ] T118 [P] Contract test for GET /trees/trash in tests/contract/test_trees_api.py
- [ ] T119 [P] Contract test for POST /trees/{id}/restore in tests/contract/test_trees_api.py
- [ ] T120 [P] Contract test for DELETE /trees/{id}/permanent in tests/contract/test_trees_api.py

### Integration Tests for Trash (TDD - Red)

- [ ] T121 [P] Integration test for soft delete and restore workflow in tests/integration/test_trash_workflow.py
- [ ] T122 [P] Integration test for permanent delete in tests/integration/test_trash_workflow.py

### Implementation for Trash (TDD - Green)

- [ ] T123 Implement TrashService in src/trees/services/trash_service.py (soft delete, restore, permanent delete)
- [ ] T124 Add trash endpoints to JosekiTreeViewSet in src/trees/views.py
- [ ] T125 Create management command for auto-cleanup (30 days) in src/trees/management/commands/cleanup_trash.py
- [ ] T126 Verify all Trash contract tests pass
- [ ] T127 Verify all Trash integration tests pass

**Checkpoint**: Trash & Recovery complete

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: パフォーマンス検証、ドキュメント、最終調整

### Performance Tests

- [ ] T128 [P] Performance test for SC-002 (100 nodes, 1s response) in tests/integration/test_performance.py
- [ ] T129 [P] Performance test for SC-003 (1000 nodes search, 2s response) in tests/integration/test_performance.py
- [ ] T130 [P] Performance test for SC-005 (100 moves KIF import, 3s) in tests/integration/test_performance.py

### Documentation & Validation

- [ ] T131 [P] Generate OpenAPI schema and validate against contracts/openapi.yaml
- [ ] T132 [P] Update quickstart.md with actual setup commands if needed
- [ ] T133 Run full test suite and ensure 100% pass rate
- [ ] T134 Run linting (ruff) and formatting (black) checks
- [ ] T135 Run type checking (mypy) and fix any issues

### Final Validation

- [ ] T136 Execute quickstart.md validation (end-to-end manual test)
- [ ] T137 Code cleanup and refactoring (remove dead code, improve naming)

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup) ──► Phase 2 (Foundational) ──┬──► Phase 3 (US1) ──► Phase 4 (US2)
                                             │
                                             ├──► Phase 5 (US3)
                                             │
                                             ├──► Phase 6 (US4)
                                             │
                                             └──► Phase 7 (US5)

All User Stories ──► Phase 8 (Trash) ──► Phase 9 (Polish)
```

### User Story Dependencies

| Story | Depends On | Can Run In Parallel With |
|-------|------------|--------------------------|
| US1 (P1) | Foundational | - (MVP, first) |
| US2 (P1) | Foundational, US1 nodes | US3, US4, US5 |
| US3 (P2) | Foundational, US1 tree structure | US2, US4, US5 |
| US4 (P2) | Foundational, US1 tree structure | US2, US3, US5 |
| US5 (P3) | Foundational, US1 nodes | US2, US3, US4 |

### Within Each User Story (TDD Order)

1. Contract tests (Red) - can run in parallel
2. Integration tests (Red) - can run in parallel
3. Serializers - can run in parallel
4. Services - sequential (may depend on each other)
5. Views - sequential (depends on services)
6. URL routing
7. Verify tests pass (Green)

---

## Parallel Execution Examples

### Phase 2: Foundational - Model Tests

```bash
# Launch all model tests in parallel (Red phase):
pytest tests/unit/test_models.py::test_joseki_tree &
pytest tests/unit/test_models.py::test_node &
pytest tests/unit/test_models.py::test_edge &
pytest tests/unit/test_models.py::test_label &
pytest tests/unit/test_models.py::test_node_label &
wait
```

### Phase 3: User Story 1 - Contract Tests

```bash
# Launch all US1 contract tests in parallel (Red phase):
pytest tests/contract/test_trees_api.py &
pytest tests/contract/test_nodes_api.py &
wait
```

### Multiple User Stories in Parallel

```bash
# After Foundational complete, different developers can work on:
# Developer A: User Story 1 (MVP)
# Developer B: User Story 2 (after US1 nodes exist)
# Developer C: User Story 4 (after US1 tree structure exists)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
   - `curl -X POST /api/v1/trees/ -d '{"name": "矢倉"}'`
   - `curl -X POST /api/v1/trees/{id}/nodes/{root_id}/moves/ -d '{"move_usi": "7g7f"}'`
5. Deploy/demo if ready

### Incremental Delivery

1. Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → **MVP Ready!**
3. Add User Story 2 → Test independently → ラベル機能追加
4. Add User Story 3 → Test independently → 深さ制限付き取得
5. Add User Story 4 → Test independently → インポート・エクスポート
6. Add User Story 5 → Test independently → コメント機能
7. Add Trash functionality → 完全なデータ保護
8. Polish → Production ready

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- **TDD Required**: Tests MUST be written and FAIL before implementation (Constitution V)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
