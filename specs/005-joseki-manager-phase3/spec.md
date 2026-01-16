# Feature Specification: Phase 3 - 定跡ツリーの作成と手順入力 (MVP)

**Feature Branch**: `005-joseki-manager-phase3`
**Created**: 2026-01-16
**Status**: Draft
**Input**: Issue #19 - User Story 1: 定跡ツリーを作成し、初期局面から分岐する手順を木構造形式で入力できる

## 概要

将棋定跡管理アプリケーション（Joseki Manager）の Phase 3 として、MVP（最小限の価値を提供する製品）を実装する。
この Phase では User Story 1「定跡ツリーの作成と手順入力」を完成させ、ユーザーが定跡ツリーを作成・管理できるようにする。

Phase 2 で構築したコアインフラ（モデル、cshogi 連携、ファクトリ）を基盤として、REST API エンドポイントを実装し、
定跡ツリーの CRUD 操作と指し手の追加・管理機能を提供する。

## User Scenarios & Testing *(mandatory)*

### User Story 1 - 定跡ツリーの新規作成 (Priority: P1)

ユーザー（将棋学習者）は、新しい定跡ツリーを作成できる。作成時に名前を指定し、初期局面（平手）をルートノードとした空の定跡ツリーが生成される。

**Why this priority**: 定跡管理の最初のステップであり、これがないと手順入力ができない。

**Independent Test**: `POST /api/v1/trees/` で定跡ツリーを作成し、ルートノードが初期局面で作成されることを確認。

**Acceptance Scenarios**:

1. **Given** API が起動している状態、**When** `POST /trees/` に `{"name": "矢倉"}` を送信、**Then** 201 Created が返され、id、name、root_node（初期局面 SFEN）を含むレスポンスが返る
2. **Given** API が起動している状態、**When** `POST /trees/` に name なしで送信、**Then** 400 Bad Request が返され、バリデーションエラーメッセージが返る
3. **Given** 定跡ツリーが作成された状態、**When** `GET /trees/{id}` を呼び出す、**Then** 作成したツリーの詳細（root_node を含む）が返る

---

### User Story 2 - 定跡ツリーの一覧・更新・取得 (Priority: P1)

ユーザーは作成した定跡ツリーの一覧を取得でき、名前や説明を更新できる。

**Why this priority**: ツリーの管理・整理に必要な基本機能。

**Independent Test**: 複数のツリーを作成し、一覧取得・個別取得・更新が正しく動作することを確認。

**Acceptance Scenarios**:

1. **Given** 複数の定跡ツリーが存在する状態、**When** `GET /trees/` を呼び出す、**Then** アクティブなツリーの一覧（id, name, node_count, created_at, updated_at）が返る
2. **Given** 定跡ツリーが存在する状態、**When** `PATCH /trees/{id}` に `{"name": "角換わり"}` を送信、**Then** 名前が更新され、updated_at が更新される
3. **Given** 存在しない tree_id を指定、**When** `GET /trees/{id}` を呼び出す、**Then** 404 Not Found が返る

---

### User Story 3 - 指し手の追加と分岐作成 (Priority: P1)

ユーザーは任意のノード（局面）から合法手を追加でき、同じ局面から複数の応手を登録することで分岐を作成できる。

**Why this priority**: 定跡ツリーの核心機能であり、手順を木構造で管理するための必須機能。

**Independent Test**: ルートノードから複数の指し手を追加し、分岐が正しく作成されることを確認。

**Acceptance Scenarios**:

1. **Given** 定跡ツリーのルートノード（初期局面）を選択した状態、**When** `POST /nodes/{id}/moves` に `{"move_usi": "7g7f"}` を送信、**Then** 201 Created が返され、新しいノード（76歩後の局面）とエッジが作成される
2. **Given** 既に子ノードが存在するノードを選択した状態、**When** 別の指し手 `{"move_usi": "2g2f"}` を送信、**Then** 分岐として新しい子ノードが追加される
3. **Given** 指し手追加後の状態、**When** `GET /nodes/{id}/children` を呼び出す、**Then** 全ての子ノード（分岐）が指し手情報（USI、日本語表記）とともに返る

---

### User Story 4 - 反則手の拒否 (Priority: P1)

システムは不正な指し手（二歩、打ち歩詰め、移動不可能な手など）を検出し、登録を拒否する。

**Why this priority**: データの整合性を保つための必須機能。不正な定跡データは学習に悪影響を与える。

**Independent Test**: 反則手を入力し、適切なエラーメッセージが返ることを確認。

**Acceptance Scenarios**:

1. **Given** 初期局面を選択した状態、**When** 不正な指し手 `{"move_usi": "1a1b"}` を送信、**Then** 400 Bad Request と `illegal_move` エラーが返る
2. **Given** 歩が既に存在する筋で、**When** 同じ筋に歩を打つ手を送信、**Then** 400 Bad Request と `nifu` エラーが返る
3. **Given** 存在しないノード ID を指定、**When** 指し手を追加しようとする、**Then** 404 Not Found が返る

---

### User Story 5 - 転置（同一局面）の検出と合流 (Priority: P1)

システムは異なる手順で同一局面に到達した場合（転置）を自動検出し、既存のノードにリンクする。

**Why this priority**: 定跡の効率的な管理に必要。転置を別ノードとして管理すると、データの重複と不整合が発生する。

**Independent Test**: 異なる手順で同一局面に到達させ、転置が検出されて既存ノードにリンクされることを確認。

**Acceptance Scenarios**:

1. **Given** 初手76歩→34歩の手順で進んだ状態、**When** 別の手順（26歩→34歩→76歩）で同一局面に到達する手を追加、**Then** 既存ノードへのリンク（転置）として追加され、`is_transposition: true` が返る
2. **Given** 転置が検出された状態、**When** 子ノードの詳細を取得、**Then** 複数の親ノード（parents）が返る
3. **Given** 転置により複数の親を持つノードがある状態、**When** `GET /nodes/{id}` を呼び出す、**Then** 全ての親エッジ情報が返る

---

### User Story 6 - ノードの削除（エッジ削除含む） (Priority: P2)

ユーザーは不要なノードを削除できる。転置により複数の親を持つノードの場合は、選択した親からのエッジのみを削除する。

**Why this priority**: 誤入力の修正やツリーの整理に必要だが、追加・取得機能より優先度は低い。

**Independent Test**: ノードを削除し、子孫ノードも含めて削除されることを確認。転置ノードの場合はエッジのみ削除されることを確認。

**Acceptance Scenarios**:

1. **Given** 子ノードが存在するノードを選択した状態、**When** `DELETE /nodes/{id}` を呼び出す、**Then** 204 No Content が返され、選択ノードと子孫ノードが削除される
2. **Given** 転置により複数の親を持つノードがある状態、**When** 特定の親からのエッジを削除、**Then** エッジのみ削除され、ノード自体は残る
3. **Given** ルートノードを選択した状態、**When** `DELETE /nodes/{id}` を呼び出す、**Then** 400 Bad Request が返される（ルートノードは削除不可）

---

### Edge Cases

- 同じノードから同じ指し手を2回追加しようとした場合は？→ 409 Conflict エラーを返す
- 極端に深いツリー（100手以上）の場合のパフォーマンスは？→ 深さ制限付きレスポンス（デフォルト 10 手、最大 50 手）
- SFEN 文字列が不正な形式でノード作成を試みた場合は？→ バリデーションエラー（内部処理のため通常発生しない）
- ツリー全体のノード数が 1000 を超えた場合は？→ API 応答が 1 秒以内であることを検証（SC-002）
- 並行リクエストで同時に同じ指し手を追加した場合は？→ データベースの一意制約により、後続リクエストが 409 Conflict

## Requirements *(mandatory)*

### Functional Requirements

以下の機能要件は `specs/002-joseki-manager/spec.md` から Phase 3 に関連するものを抽出。

- **FR-001**: System MUST 平手の初期局面から定跡ツリーを新規作成できる
- **FR-002**: System MUST 任意のノードに対して合法手のみを子ノードとして追加できる
- **FR-003**: System MUST 同一局面から複数の分岐（応手）を登録できる
- **FR-004**: System MUST 定跡ツリーのデータを永続化し、再起動後も利用できる
- **FR-007**: System MUST 定跡ツリーを木構造形式で表現するデータ構造を提供する
- **FR-008**: System MUST 各ノードにおける局面（盤面と持ち駒）のデータを提供する
- **FR-012**: System MUST 同一局面への異なる手順経路（転置）を検出し、合流を許可する
- **FR-013**: System MUST 反則手の入力を検出しエラーを表示する

### Key Entities

このフェーズで操作するエンティティ（Phase 2 で実装済み）:

- **JosekiTree（定跡ツリー）**: 定跡体系の管理単位。name, description, is_deleted, deleted_at を持つ
- **Node（ノード）**: 局面を表す。tree_id, sfen, ply, comment を持つ。転置により複数の親を持つ可能性あり
- **Edge（エッジ）**: 親子ノード間の指し手を表す。parent_id, child_id, move_usi, move_japanese を持つ

## Success Criteria *(mandatory)*

### Measurable Outcomes

Phase 3 完了時に検証する成功基準:

- **SC-001**: 全 Contract Tests がパスする（T036〜T041b）
- **SC-002**: 全 Integration Tests がパスする（T042〜T045b）
- **SC-003**: 定跡ツリーの CRUD 操作（作成、取得、更新、一覧）が正常に動作する
- **SC-004**: 合法手のみが追加でき、反則手は拒否される
- **SC-005**: 転置（同一局面への異なる手順経路）が検出され、既存ノードにリンクされる
- **SC-006**: ノード削除時、転置ノードはエッジのみ削除、単一親ノードは子孫含め削除される
- **SC-007**: 100ノード以上の定跡ツリーでも、API応答が1秒以内に完了する（002-joseki-manager SC-002）

## Assumptions

- Phase 2（Issue #18）が完了しており、モデル、cshogi 連携、ファクトリが実装済み
- PostgreSQL がローカルで稼働している
- uv を使用した依存関係管理が設定済み
- TDD（テスト駆動開発）アプローチで実装する（Red-Green-Refactor サイクル）

## Related Documents

- 設計ブランチ: `002-joseki-manager`
- [spec.md](../002-joseki-manager/spec.md) - 機能仕様（全体）
- [plan.md](../002-joseki-manager/plan.md) - 実装計画
- [data-model.md](../002-joseki-manager/data-model.md) - データモデル定義
- [openapi.yaml](../002-joseki-manager/contracts/openapi.yaml) - API 契約
- [tasks.md](../002-joseki-manager/tasks.md) - タスク一覧（T036〜T057）
- Phase 2 仕様: [spec.md](../004-joseki-manager-phase2/spec.md)

## タスク一覧（Issue #19 より）

### Contract Tests (TDD - Red)

- [ ] T036 Contract test for POST /trees
- [ ] T037 Contract test for GET /trees/{id}
- [ ] T038 Contract test for GET /trees
- [ ] T039 Contract test for PATCH /trees/{id}
- [ ] T040 Contract test for POST /nodes/{id}/moves
- [ ] T041 Contract test for GET /nodes/{id}/children
- [ ] T041b Contract test for DELETE /nodes/{id}

### Integration Tests (TDD - Red)

- [ ] T042 Integration test for tree creation with root node
- [ ] T043 Integration test for adding moves and creating branches
- [ ] T044 Integration test for transposition detection
- [ ] T045 Integration test for illegal move rejection
- [ ] T045b Integration test for deleting edge from transposition node

### Implementation (TDD - Green)

- [ ] T046 Create JosekiTreeSerializer
- [ ] T047 Create NodeSerializer
- [ ] T048 Create EdgeSerializer
- [ ] T049 Create MoveCreateSerializer
- [ ] T050 Implement TreeService
- [ ] T051 Implement NodeService
- [ ] T052 Implement JosekiTreeViewSet
- [ ] T053 Implement NodeViewSet
- [ ] T054 Configure URL routing in src/trees/urls.py
- [ ] T055 Register trees URLs in src/joseki/urls.py
- [ ] T056 Verify all US1 contract tests pass
- [ ] T057 Verify all US1 integration tests pass

## API Endpoints (Phase 3 Scope)

Phase 3 で実装するエンドポイント（`contracts/openapi.yaml` より）:

| Method | Endpoint | Description |
| ------ | -------- | ----------- |
| POST | /trees | 定跡ツリー作成 |
| GET | /trees | 定跡ツリー一覧取得 |
| GET | /trees/{tree_id} | 定跡ツリー詳細取得 |
| PATCH | /trees/{tree_id} | 定跡ツリー更新 |
| POST | /trees/{tree_id}/nodes/{node_id}/moves | 指し手追加 |
| GET | /trees/{tree_id}/nodes/{node_id}/children | 子ノード一覧取得 |
| DELETE | /trees/{tree_id}/nodes/{node_id} | ノード削除 |
| GET | /trees/{tree_id}/nodes/{node_id} | ノード詳細取得 |
