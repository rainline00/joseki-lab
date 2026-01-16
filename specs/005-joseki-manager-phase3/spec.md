# Feature Specification: Phase 3 - 定跡ツリーの作成と手順入力 (MVP)

**Feature Branch**: `005-joseki-manager-phase3`
**Created**: 2026-01-16
**Status**: Draft
**Base**: [002-joseki-manager/spec.md](../002-joseki-manager/spec.md)

## 概要

Phase 3 は Joseki Manager の **MVP（最小限の価値を提供する製品）** を実装する。ユーザーは定跡ツリーを作成し、初期局面から分岐する手順を木構造形式で入力できるようになる。

## 依存関係

- **Phase 2 (Foundational)** が完了していること（#18）
  - モデル: JosekiTree, Node, Edge, Label, NodeLabel
  - ファクトリ: JosekiTreeFactory, NodeFactory, EdgeFactory, LabelFactory
  - cshogi 統合: position.py, rules.py

## User Stories

### US1-1: 定跡ツリーの新規作成 (Priority: P1)

ユーザーは新しい定跡ツリーを作成できる。ツリー作成時に平手初期局面をルートノードとして自動作成する。

**Acceptance Scenarios**:
1. **Given** 有効な名前を含むリクエスト、**When** POST /trees を実行、**Then** 201 が返り、ルートノード（初期局面）が自動作成される
2. **Given** 名前が空のリクエスト、**When** POST /trees を実行、**Then** 400 エラーが返る
3. **Given** 作成されたツリー、**When** GET /trees/{id} を実行、**Then** ルートノードを含むツリー詳細が返る

---

### US1-2: 定跡ツリーの一覧・更新・取得 (Priority: P1)

ユーザーは定跡ツリーの一覧を取得し、個々のツリーの名前や説明を更新できる。

**Acceptance Scenarios**:
1. **Given** 複数の定跡ツリーが存在、**When** GET /trees を実行、**Then** アクティブなツリー一覧が返る
2. **Given** 既存のツリー、**When** PATCH /trees/{id} で名前を更新、**Then** 200 が返り名前が更新される
3. **Given** 存在しないツリーID、**When** GET /trees/{id} を実行、**Then** 404 エラーが返る

---

### US1-3: 指し手の追加と分岐作成 (Priority: P1)

ユーザーは任意のノードから指し手を追加し、子ノードを作成できる。同じノードから複数の指し手を追加することで分岐を作成できる。

**Acceptance Scenarios**:
1. **Given** ルートノード、**When** POST /nodes/{id}/moves で合法手（7g7f）を追加、**Then** 201 が返り子ノードが作成される
2. **Given** 既に子ノードが存在するノード、**When** 別の合法手（2g2f）を追加、**Then** 201 が返り分岐として新しい子ノードが作成される
3. **Given** 既に同じ指し手が存在、**When** 同じ指し手を追加、**Then** 409 Conflict が返る
4. **Given** ノード、**When** GET /nodes/{id}/children を実行、**Then** 子ノード一覧が指し手情報付きで返る

---

### US1-4: 反則手の拒否 (Priority: P1)

システムは反則手（不正な指し手）の入力を検出し、エラーを返す。

**Acceptance Scenarios**:
1. **Given** ルートノード、**When** 不正な指し手（例: 1a1a）を追加、**Then** 400 エラーが返り、エラー種別が `invalid_format` と表示される
2. **Given** ルートノード、**When** 合法でない指し手（例: 9i9h - 存在しない駒）を追加、**Then** 400 エラーが返り、エラー種別が `illegal_move` と表示される
3. **Given** 二歩が発生する局面、**When** 二歩となる指し手を追加、**Then** 400 エラーが返り、エラー種別が `illegal_move` と表示される

---

### US1-5: 転置（同一局面）の検出と合流 (Priority: P1)

異なる手順で同一局面に到達した場合（転置）、システムは既存ノードを検出し、新しいエッジのみを作成して合流させる。

**Acceptance Scenarios**:
1. **Given** 手順 A→B→C で到達した局面 X が存在、**When** 手順 A→D→E で同じ局面 X に到達する指し手を追加、**Then** 新しいノードは作成されず、既存ノード X へのエッジのみ作成される
2. **Given** 転置が発生した場合、**When** レスポンスを確認、**Then** `is_transposition: true` が返る
3. **Given** 転置ノード（複数の親を持つ）、**When** GET /nodes/{id} を実行、**Then** 複数の親エッジ情報が返る

---

### US1-6: ノードの削除 (Priority: P2)

ユーザーはノードを削除できる。単一親のノードは子孫含め削除され、転置ノード（複数親）は選択した親からのエッジのみ削除される。

**Acceptance Scenarios**:
1. **Given** 単一親のノード、**When** DELETE /nodes/{id} を実行、**Then** 204 が返り、ノードと子孫が削除される
2. **Given** 転置ノード（複数の親）、**When** DELETE /nodes/{id}?parent_id={parent_id} を実行、**Then** 204 が返り、指定した親からのエッジのみ削除される
3. **Given** ルートノード、**When** DELETE /nodes/{id} を実行、**Then** 400 エラーが返る（ルートノードは削除不可）

---

## Functional Requirements（対象）

Phase 3 で実装する機能要件:

- **FR-001**: 平手の初期局面から定跡ツリーを新規作成できる
- **FR-002**: 任意のノードに対して合法手のみを子ノードとして追加できる
- **FR-003**: 同一局面から複数の分岐（応手）を登録できる
- **FR-004**: 定跡ツリーのデータを永続化し、再起動後も利用できる
- **FR-007**: 定跡ツリーを木構造形式で表現するデータ構造を提供する
- **FR-008**: 各ノードにおける局面のデータを提供する
- **FR-012**: 同一局面への異なる手順経路（転置）を検出し、合流を許可する
- **FR-013**: 反則手の入力を検出しエラーを表示する

---

## API エンドポイント

Phase 3 で実装するエンドポイント（[openapi.yaml](../002-joseki-manager/contracts/openapi.yaml) より抜粋）:

| Method | Path | Description | FR |
|--------|------|-------------|-----|
| POST | /trees | 定跡ツリー作成 | FR-001 |
| GET | /trees | 定跡ツリー一覧 | FR-004 |
| GET | /trees/{tree_id} | 定跡ツリー詳細 | FR-007, FR-008 |
| PATCH | /trees/{tree_id} | 定跡ツリー更新 | FR-004 |
| POST | /trees/{tree_id}/nodes/{node_id}/moves | 指し手追加 | FR-002, FR-003, FR-012, FR-013 |
| GET | /trees/{tree_id}/nodes/{node_id}/children | 子ノード一覧 | FR-007 |
| DELETE | /trees/{tree_id}/nodes/{node_id} | ノード削除 | - |

---

## Success Criteria

- **SC-001**: 全 Contract Tests がパスする（T036-T041b）
- **SC-002**: 全 Integration Tests がパスする（T042-T045b）
- **SC-003**: 100ノード以上の定跡ツリーでも API 応答が1秒以内に完了する（元 SC-002）
- **SC-004**: 定跡ツリーの CRUD 操作（作成・取得・更新・一覧）ができる
- **SC-005**: 合法手のみが追加できる（反則手は適切なエラーで拒否）
- **SC-006**: 転置（同一局面）が検出され、既存ノードへ合流する
- **SC-007**: ノード削除が正しく動作する（単一親・転置対応）

---

## Edge Cases

- 同じ指し手の重複追加 → 409 Conflict を返す
- 存在しない tree_id/node_id → 404 Not Found を返す
- ルートノードの削除 → 400 Bad Request を返す
- 転置ノード削除時に parent_id 未指定 → 400 Bad Request（parent_id 必須）
- 空の名前でツリー作成 → 400 Bad Request を返す

---

## Clarifications

### Session 2026-01-16

- Q: 転置ノード削除時の振る舞いは？ → A: `parent_id` クエリパラメータで指定した親からのエッジのみ削除。parent_id 未指定かつ複数親がある場合は 400 エラー
- Q: 指し手追加時の手数（ply）はどう計算？ → A: 親ノードの ply + 1 で自動計算
- Q: GET /trees/{id} の depth パラメータは Phase 3 で実装？ → A: Phase 3 では depth パラメータなしの基本実装のみ。depth 制限は Phase 5 (US3) で実装

---

## References

- [002-joseki-manager/spec.md](../002-joseki-manager/spec.md) - 全体仕様
- [002-joseki-manager/contracts/openapi.yaml](../002-joseki-manager/contracts/openapi.yaml) - API 仕様
- [002-joseki-manager/tasks.md](../002-joseki-manager/tasks.md) - 全体タスク一覧（Phase 3: T036-T057）
- [004-joseki-manager-phase2/](../004-joseki-manager-phase2/) - Phase 2 成果物
