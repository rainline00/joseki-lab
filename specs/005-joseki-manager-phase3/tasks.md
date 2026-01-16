# Tasks: Phase 3 - 定跡ツリーの作成と手順入力 (MVP)

**Input**: Design documents from `/specs/005-joseki-manager-phase3/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/openapi-phase3.md, quickstart.md, research.md

**Tests**: Constitution V (TDD) に従い、すべての実装タスクにテストタスクを含む。Red-Green-Refactor サイクルを徹底。

**Organization**: Phase 3 は MVP として 6 つのサブストーリー（US1-1〜US1-6）を含む。すべて同一 Phase で実装。

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: User Story 1 内のサブストーリー（US1-1〜US1-6）
- Include exact file paths in descriptions

## Path Conventions

- Django project: `src/joseki/` (settings), `src/trees/`, `src/core/`
- Tests: `tests/unit/`, `tests/integration/`, `tests/contract/`

---

## Phase 3.0: Prerequisites Verification

**Purpose**: Phase 2 の成果物が利用可能であることを確認

- [ ] T001 Verify JosekiTree, Node, Edge models exist in src/trees/models.py
- [ ] T002 Verify cshogi integration exists in src/core/shogi/position.py and src/core/shogi/rules.py
- [ ] T003 Verify factories exist in tests/factories.py
- [ ] T004 Run existing unit tests to ensure foundation is stable (`pytest tests/unit/`)

---

## Phase 3.1: Contract Tests (TDD - Red)

**Purpose**: API 契約テストを作成し、失敗することを確認

### Trees API Contract Tests

- [ ] T005 [P] [US1-1] Contract test for POST /trees in tests/contract/test_trees_api.py (201, 400)
- [ ] T006 [P] [US1-1] Contract test for POST /trees with empty name (400) in tests/contract/test_trees_api.py
- [ ] T007 [P] [US1-2] Contract test for GET /trees in tests/contract/test_trees_api.py (200)
- [ ] T008 [P] [US1-2] Contract test for GET /trees/{id} in tests/contract/test_trees_api.py (200, 404)
- [ ] T009 [P] [US1-2] Contract test for PATCH /trees/{id} in tests/contract/test_trees_api.py (200, 404)

### Nodes API Contract Tests

- [ ] T010 [P] [US1-3] Contract test for POST /trees/{tree_id}/nodes/{node_id}/moves in tests/contract/test_nodes_api.py (201)
- [ ] T011 [P] [US1-3] Contract test for POST /nodes/{id}/moves with duplicate move (409) in tests/contract/test_nodes_api.py
- [ ] T012 [P] [US1-3] Contract test for GET /trees/{tree_id}/nodes/{node_id}/children in tests/contract/test_nodes_api.py (200)
- [ ] T013 [P] [US1-4] Contract test for POST /nodes/{id}/moves with invalid format (400 invalid_format) in tests/contract/test_nodes_api.py
- [ ] T014 [P] [US1-4] Contract test for POST /nodes/{id}/moves with illegal move (400 illegal_move) in tests/contract/test_nodes_api.py
- [ ] T015 [P] [US1-5] Contract test for POST /nodes/{id}/moves detecting transposition in tests/contract/test_nodes_api.py
- [ ] T016 [P] [US1-6] Contract test for DELETE /trees/{tree_id}/nodes/{node_id} (single parent) in tests/contract/test_nodes_api.py (204)
- [ ] T017 [P] [US1-6] Contract test for DELETE /trees/{tree_id}/nodes/{node_id}?parent_id= (transposition) in tests/contract/test_nodes_api.py
- [ ] T018 [P] [US1-6] Contract test for DELETE /nodes/{id} root node (400 cannot_delete_root) in tests/contract/test_nodes_api.py
- [ ] T019 [P] [US1-6] Contract test for DELETE /nodes/{id} transposition without parent_id (400 parent_id_required) in tests/contract/test_nodes_api.py

**Checkpoint**: All contract tests written and failing (Red phase complete)

---

## Phase 3.2: Integration Tests (TDD - Red)

**Purpose**: 統合テストを作成し、失敗することを確認

- [ ] T020 [P] [US1-1] Integration test for tree creation with auto root node in tests/integration/test_tree_workflow.py
- [ ] T021 [P] [US1-2] Integration test for tree CRUD operations in tests/integration/test_tree_workflow.py
- [ ] T022 [P] [US1-3] Integration test for adding moves and creating branches in tests/integration/test_tree_workflow.py
- [ ] T023 [P] [US1-4] Integration test for illegal move rejection (nifu, invalid format) in tests/integration/test_tree_workflow.py
- [ ] T024 [P] [US1-5] Integration test for transposition detection and merging in tests/integration/test_tree_workflow.py
- [ ] T025 [P] [US1-6] Integration test for node deletion (single parent, cascading) in tests/integration/test_tree_workflow.py
- [ ] T026 [P] [US1-6] Integration test for transposition node edge deletion in tests/integration/test_tree_workflow.py

**Checkpoint**: All integration tests written and failing (Red phase complete)

---

## Phase 3.3: Serializers (TDD - Green)

**Purpose**: DRF Serializer を実装

- [ ] T027 [P] [US1-1] Create JosekiTreeCreateSerializer in src/trees/serializers.py
- [ ] T028 [P] [US1-2] Create JosekiTreeUpdateSerializer in src/trees/serializers.py
- [ ] T029 [P] [US1-2] Create JosekiTreeSummarySerializer in src/trees/serializers.py
- [ ] T030 [P] [US1-2] Create JosekiTreeSerializer (with root_node) in src/trees/serializers.py
- [ ] T031 [P] [US1-3] Create NodeSerializer in src/trees/serializers.py
- [ ] T032 [P] [US1-3] Create NodeDetailSerializer (with parents/children) in src/trees/serializers.py
- [ ] T033 [P] [US1-3] Create EdgeSerializer in src/trees/serializers.py
- [ ] T034 [P] [US1-3] Create MoveCreateSerializer in src/trees/serializers.py
- [ ] T035 [P] [US1-3] Create MoveResultSerializer in src/trees/serializers.py
- [ ] T036 [P] [US1-3] Create ChildNodeSerializer in src/trees/serializers.py
- [ ] T037 [P] [US1-4] Create MoveErrorSerializer in src/trees/serializers.py

---

## Phase 3.4: Services (TDD - Green)

**Purpose**: ビジネスロジックを Service 層に実装

### TreeService

- [ ] T038 Create src/trees/services/__init__.py
- [ ] T039 [US1-1] Implement TreeService.create_tree (with auto root node) in src/trees/services/tree_service.py
- [ ] T040 [US1-2] Implement TreeService.get_tree in src/trees/services/tree_service.py
- [ ] T041 [US1-2] Implement TreeService.list_trees in src/trees/services/tree_service.py
- [ ] T042 [US1-2] Implement TreeService.update_tree in src/trees/services/tree_service.py

### NodeService

- [ ] T043 [US1-3] Implement NodeService.add_move in src/trees/services/node_service.py
- [ ] T044 [US1-3] Implement NodeService.get_children in src/trees/services/node_service.py
- [ ] T045 [US1-4] Add move validation (InvalidMoveError, IllegalMoveError) in NodeService.add_move
- [ ] T046 [US1-5] Implement transposition detection in NodeService.add_move
- [ ] T047 [US1-6] Implement NodeService.delete_node (single parent) in src/trees/services/node_service.py
- [ ] T048 [US1-6] Implement NodeService.delete_node (transposition with parent_id) in src/trees/services/node_service.py
- [ ] T049 [US1-3] Implement DuplicateMoveError exception in src/trees/services/node_service.py

---

## Phase 3.5: ViewSets (TDD - Green)

**Purpose**: DRF ViewSet を実装

### JosekiTreeViewSet

- [ ] T050 [US1-1] Implement JosekiTreeViewSet.create in src/trees/views.py
- [ ] T051 [US1-2] Implement JosekiTreeViewSet.list in src/trees/views.py
- [ ] T052 [US1-2] Implement JosekiTreeViewSet.retrieve in src/trees/views.py
- [ ] T053 [US1-2] Implement JosekiTreeViewSet.partial_update in src/trees/views.py

### NodeViewSet

- [ ] T054 [US1-3] Implement NodeViewSet.add_move (@action) in src/trees/views.py
- [ ] T055 [US1-3] Implement NodeViewSet.children (@action) in src/trees/views.py
- [ ] T056 [US1-6] Implement NodeViewSet.destroy in src/trees/views.py

### Exception Handlers

- [ ] T057 [US1-4] Create custom exception handler for InvalidMoveError/IllegalMoveError in src/trees/views.py
- [ ] T058 [US1-3] Create custom exception handler for DuplicateMoveError (409) in src/trees/views.py

---

## Phase 3.6: URL Routing

**Purpose**: URL ルーティングを設定

- [ ] T059 Create src/trees/urls.py with DefaultRouter for trees
- [ ] T060 Add custom routes for node actions (/nodes/{id}/moves, /children) in src/trees/urls.py
- [ ] T061 Add node detail and delete routes in src/trees/urls.py
- [ ] T062 Register trees URLs in src/joseki/urls.py under /api/v1/

---

## Phase 3.7: Test Verification (TDD - Green Complete)

**Purpose**: すべてのテストがパスすることを確認

- [ ] T063 Verify all contract tests pass (`pytest tests/contract/ -v`)
- [ ] T064 Verify all integration tests pass (`pytest tests/integration/ -v`)
- [ ] T065 Verify all existing unit tests still pass (`pytest tests/unit/ -v`)
- [ ] T066 Run full test suite (`pytest -v`)

---

## Phase 3.8: Validation & Documentation

**Purpose**: 最終検証とドキュメント更新

- [ ] T067 Manual API test: Create tree via curl (per quickstart.md)
- [ ] T068 Manual API test: Add moves and create branch
- [ ] T069 Manual API test: Verify transposition detection
- [ ] T070 Manual API test: Verify illegal move rejection
- [ ] T071 Manual API test: Verify node deletion
- [ ] T072 Run linting (`ruff check src/`)
- [ ] T073 Run formatting check (`black --check src/`)

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 3.0 (Prerequisites) ──► Phase 3.1 (Contract Tests) ──► Phase 3.2 (Integration Tests)
                                                                       │
                                                                       ▼
Phase 3.3 (Serializers) ──► Phase 3.4 (Services) ──► Phase 3.5 (ViewSets) ──► Phase 3.6 (URL Routing)
                                                                                       │
                                                                                       ▼
                                                        Phase 3.7 (Test Verification) ──► Phase 3.8 (Validation)
```

### Within Each Phase

- [P] タスクは並列実行可能（異なるファイル、依存関係なし）
- 非 [P] タスクは順次実行（依存関係あり）

### Story Dependencies

| Story | Description | Dependencies |
|-------|-------------|--------------|
| US1-1 | 定跡ツリー新規作成 | None (first) |
| US1-2 | ツリー一覧・更新・取得 | US1-1 |
| US1-3 | 指し手追加と分岐作成 | US1-1 |
| US1-4 | 反則手の拒否 | US1-3 |
| US1-5 | 転置検出と合流 | US1-3 |
| US1-6 | ノード削除 | US1-3, US1-5 |

---

## Parallel Execution Examples

### Phase 3.1: Contract Tests (All Parallel)

```bash
# Launch all contract tests in parallel:
pytest tests/contract/test_trees_api.py &
pytest tests/contract/test_nodes_api.py &
wait
```

### Phase 3.3: Serializers (All Parallel)

```bash
# All serializers can be created in parallel (same file, but independent classes)
# Or split into separate tasks for true parallelism
```

---

## Implementation Strategy

### TDD Workflow

1. **Red Phase**: Write all contract tests (T005-T019) and integration tests (T020-T026)
2. **Verify Red**: Run tests, confirm they all fail
3. **Green Phase**: Implement serializers, services, views in order
4. **Verify Green**: Run tests after each implementation group
5. **Refactor**: Clean up code while keeping tests green

### MVP Checkpoint

After Phase 3.7 completion:
- 定跡ツリーの CRUD 操作が機能する
- 指し手追加と分岐作成が機能する
- 反則手が拒否される
- 転置が検出される
- ノード削除が機能する

### Manual Validation (Phase 3.8)

```bash
# ツリー作成
curl -X POST http://localhost:8000/api/v1/trees/ \
  -H "Content-Type: application/json" \
  -d '{"name": "矢倉"}'

# 指し手追加（7六歩）
curl -X POST http://localhost:8000/api/v1/trees/{tree_id}/nodes/{root_id}/moves/ \
  -H "Content-Type: application/json" \
  -d '{"move_usi": "7g7f"}'

# 分岐作成（2六歩）
curl -X POST http://localhost:8000/api/v1/trees/{tree_id}/nodes/{root_id}/moves/ \
  -H "Content-Type: application/json" \
  -d '{"move_usi": "2g2f"}'
```

---

## Task Summary

| Phase | Tasks | Description |
|-------|-------|-------------|
| 3.0 | T001-T004 | Prerequisites Verification |
| 3.1 | T005-T019 | Contract Tests (Red) |
| 3.2 | T020-T026 | Integration Tests (Red) |
| 3.3 | T027-T037 | Serializers |
| 3.4 | T038-T049 | Services |
| 3.5 | T050-T058 | ViewSets |
| 3.6 | T059-T062 | URL Routing |
| 3.7 | T063-T066 | Test Verification (Green) |
| 3.8 | T067-T073 | Validation & Documentation |

**Total**: 73 tasks

---

## Success Criteria

Phase 3 完了条件（spec.md より）:

- [ ] SC-001: 全 Contract Tests がパスする
- [ ] SC-002: 全 Integration Tests がパスする
- [ ] SC-003: 100ノード以上のツリーで API 応答 1秒以内
- [ ] SC-004: 定跡ツリーの CRUD 操作ができる
- [ ] SC-005: 合法手のみが追加できる（反則手は拒否）
- [ ] SC-006: 転置（同一局面）が検出される
- [ ] SC-007: ノード削除が正しく動作する

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- **TDD Required**: Tests MUST be written and FAIL before implementation (Constitution V)
- Commit after each task or logical group
- Stop at any checkpoint to validate independently

---

## References

- [spec.md](./spec.md) - Phase 3 仕様書
- [plan.md](./plan.md) - 実装計画
- [data-model.md](./data-model.md) - Service/Serializer 設計
- [contracts/openapi-phase3.md](./contracts/openapi-phase3.md) - API 契約
- [quickstart.md](./quickstart.md) - 開発ガイド
- [research.md](./research.md) - 技術調査
