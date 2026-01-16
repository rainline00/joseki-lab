# Tasks: Phase 2 Foundational - コアインフラ構築

**Input**: Design documents from `/specs/004-joseki-manager-phase2/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/interfaces.md
**Tests**: TDD アプローチ - すべてのモデルと cshogi 連携はテスト先行で実装

**Organization**: タスクは Issue #18 のタスク番号（T011〜T035）を継承し、ユーザーストーリーごとにグループ化

## Format: `[ID] [P?] [Story] Description`

- **[P]**: 並列実行可能（異なるファイル、依存関係なし）
- **[Story]**: 所属するユーザーストーリー（US1, US2, US3, US4）
- 正確なファイルパスを含む

## Path Conventions

```
src/
├── joseki/                    # Django プロジェクト（Phase 1 で作成済み）
├── trees/                     # 定跡ツリー管理アプリ
├── labels/                    # ラベル管理アプリ
├── exports/                   # エクスポート機能アプリ
└── core/                      # 共通機能
    └── shogi/                 # 将棋ロジックラッパー

tests/
├── conftest.py                # pytest fixtures（Phase 1 で作成済み）
├── factories.py               # factory_boy ファクトリ
└── unit/                      # ユニットテスト
    ├── test_models.py
    ├── test_position.py
    └── test_rules.py
```

---

## Phase 1: Setup (Phase 1 で完了済み)

**Purpose**: プロジェクト初期化と基本構造

*Phase 1（Issue #17）で完了済み。Django プロジェクト構造が存在する前提で開始。*

---

## Phase 2: Foundational - User Story 1（Django アプリケーション作成）(Priority: P1)

**Goal**: 全モデルと機能の受け皿となる Django アプリケーション構造を作成

**Independent Test**: 各アプリケーションディレクトリが存在し、Django アプリとして認識されることを確認

### Core Infrastructure

- [x] T011 [P] [US1] Create Django app `trees` in src/trees/
- [x] T012 [P] [US1] Create Django app `labels` in src/labels/
- [x] T013 [P] [US1] Create Django app `exports` in src/exports/
- [x] T014 [P] [US1] Create Django app `core` in src/core/
- [x] T015 [US1] Create src/core/shogi/ modules (position.py, rules.py, exceptions.py, __init__.py)

**Checkpoint**: 4つの Django アプリが INSTALLED_APPS に登録され、src/core/shogi/ からモジュールがインポート可能

---

## Phase 3: User Story 2 - データモデル実装 (Priority: P1) 🎯 MVP

**Goal**: TDD アプローチで 5 つのデータモデル（JosekiTree, Node, Edge, Label, NodeLabel）を実装

**Independent Test**: 各モデルのユニットテストがパスし、マイグレーションが正常に適用される

### Tests for User Story 2 (TDD - Red Phase)

> **NOTE: これらのテストを FIRST で書き、実装前に FAIL することを確認**

- [x] T016 [P] [US2] Write failing test for JosekiTree model in tests/unit/test_models.py
- [x] T017 [P] [US2] Write failing test for Node model (including ply field and sfen_with_ply property) in tests/unit/test_models.py
- [x] T018 [P] [US2] Write failing test for Edge model (including self-reference constraint) in tests/unit/test_models.py
- [x] T019 [P] [US2] Write failing test for Label model (including HEX color validation) in tests/unit/test_models.py
- [x] T020 [P] [US2] Write failing test for NodeLabel model in tests/unit/test_models.py

### Implementation for User Story 2 (TDD - Green Phase)

- [x] T021 [US2] Implement JosekiTree model (make T016 pass) in src/trees/models.py
- [x] T022 [US2] Implement Node model (make T017 pass) in src/trees/models.py
- [x] T023 [US2] Implement Edge model (make T018 pass) in src/trees/models.py
- [x] T024 [US2] Implement Label model (make T019 pass) in src/labels/models.py
- [x] T025 [US2] Implement NodeLabel model (make T020 pass) in src/labels/models.py
- [x] T026 [US2] Create initial migrations for trees and labels apps
- [x] T027 [US2] Apply migrations and verify database schema

**Checkpoint**: 5 つのモデルが実装され、全ユニットテストがパス。マイグレーションが適用済み。

---

## Phase 4: User Story 3 - cshogi 連携実装 (Priority: P1)

**Goal**: TDD アプローチで SFEN 処理と合法手検証機能を実装

**Independent Test**: SFEN 解析テストと合法手検証テストがパス

### Tests for User Story 3 (TDD - Red Phase)

> **NOTE: これらのテストを FIRST で書き、実装前に FAIL することを確認**

- [x] T028 [P] [US3] Write failing test for SFEN handling (parse_sfen, normalize_sfen, get_initial_sfen) in tests/unit/test_position.py
- [x] T029 [P] [US3] Write failing test for move validation (is_legal_move, validate_move, get_legal_moves, apply_move) in tests/unit/test_rules.py

### Implementation for User Story 3 (TDD - Green Phase)

- [x] T030 [US3] Implement exceptions.py (ShogiError, SfenParseError, InvalidMoveError, IllegalMoveError) in src/core/shogi/exceptions.py
- [x] T031 [US3] Implement SFEN utilities (make T028 pass) in src/core/shogi/position.py
- [x] T032 [US3] Implement move validator (make T029 pass) in src/core/shogi/rules.py

**Checkpoint**: cshogi 連携が完了。SFEN 処理と合法手検証のテストがパス。

---

## Phase 5: User Story 4 - テストファクトリ作成 (Priority: P2)

**Goal**: factory_boy を使用して各モデルのファクトリを作成し、後続テストのデータ生成を簡略化

**Independent Test**: 各ファクトリでオブジェクトを生成し、データベースに保存できることを確認

### Implementation for User Story 4

- [x] T033 [P] [US4] Create JosekiTreeFactory in tests/factories.py
- [x] T034 [P] [US4] Create NodeFactory in tests/factories.py
- [x] T035 [P] [US4] Create EdgeFactory in tests/factories.py
- [x] T036 [P] [US4] Create LabelFactory in tests/factories.py
- [x] T037 [US4] Write factory tests to verify object creation in tests/unit/test_factories.py

**Checkpoint**: 4 つのファクトリが作成され、オブジェクト生成テストがパス。

---

## Phase 6: Polish & Validation

**Purpose**: 最終検証と品質確認

- [x] T038 Run all unit tests (`uv run pytest tests/unit/`)
- [x] T039 Verify all success criteria (SC-001 to SC-007) from spec.md
- [x] T040 [P] Update INSTALLED_APPS in src/joseki/settings.py if not already done

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup) - 完了済み
    ↓
Phase 2 (US1: Django Apps) - 全ストーリーをブロック
    ↓
┌─────────────────────┬─────────────────────┐
│ Phase 3 (US2: Models) │ Phase 4 (US3: cshogi) │
│     (TDD)            │       (TDD)          │
└──────────┬──────────┴──────────┬──────────┘
           ↓                     ↓
         Phase 5 (US4: Factories)
                  ↓
         Phase 6 (Polish)
```

### User Story Dependencies

- **US1 (Django Apps)**: 依存なし - 即座に開始可能
- **US2 (Models)**: US1 完了後に開始（アプリ構造が必要）
- **US3 (cshogi)**: US1 完了後に開始（core/shogi/ 構造が必要）
- **US4 (Factories)**: US2 完了後に開始（モデルが必要）

### Within Each User Story (TDD Cycle)

1. テスト作成 → FAIL 確認（Red）
2. 最小限の実装 → PASS 確認（Green）
3. リファクタリング（Refactor）
4. 次のテストへ

### Parallel Opportunities

**Phase 2 (US1)**: T011〜T014 は並列実行可能
**Phase 3 (US2) Tests**: T016〜T020 は並列実行可能
**Phase 4 (US3) Tests**: T028〜T029 は並列実行可能
**Phase 5 (US4)**: T033〜T036 は並列実行可能

---

## Parallel Example: Phase 2 (US1)

```bash
# Launch all Django app creation tasks together:
Task: "Create Django app `trees` in src/trees/"
Task: "Create Django app `labels` in src/labels/"
Task: "Create Django app `exports` in src/exports/"
Task: "Create Django app `core` in src/core/"
```

## Parallel Example: Phase 3 (US2) - Test Phase

```bash
# Launch all model tests together (Red phase):
Task: "Write failing test for JosekiTree model"
Task: "Write failing test for Node model"
Task: "Write failing test for Edge model"
Task: "Write failing test for Label model"
Task: "Write failing test for NodeLabel model"
```

---

## Implementation Strategy

### MVP First (User Story 1 + 2)

1. Complete Phase 2: US1 - Django Apps
2. Complete Phase 3: US2 - Data Models (TDD)
3. **STOP and VALIDATE**: マイグレーションが適用され、モデルテストがパス
4. 基本的なモデル操作が可能な状態

### Incremental Delivery

1. US1 完了 → Django アプリ構造が整う
2. US2 完了 → データモデルが使用可能
3. US3 完了 → cshogi 連携が使用可能
4. US4 完了 → テストファクトリが使用可能
5. 各ストーリーは独立して価値を提供

---

## Success Criteria Mapping

| SC | タスク | 検証方法 |
|----|--------|----------|
| SC-001 | T011-T014 | 4 アプリが INSTALLED_APPS に登録 |
| SC-002 | T015, T030-T032 | `from src.core.shogi import position, rules` が成功 |
| SC-003 | T016-T025 | `uv run pytest tests/unit/test_models.py` が全パス |
| SC-004 | T026-T027 | `python manage.py migrate` が成功 |
| SC-005 | T028-T032 | `uv run pytest tests/unit/test_position.py tests/unit/test_rules.py` が全パス |
| SC-006 | T033-T037 | `uv run pytest tests/unit/test_factories.py` が全パス |
| SC-007 | T038 | `uv run pytest tests/unit/` が全パス |

---

## Notes

- [P] タスク = 異なるファイル、依存関係なし
- [Story] ラベルは特定のユーザーストーリーへのトレーサビリティ用
- 各ユーザーストーリーは独立して完了・テスト可能
- TDD: テストが失敗することを確認してから実装
- 各タスクまたは論理グループ完了後にコミット
- チェックポイントで検証可能
