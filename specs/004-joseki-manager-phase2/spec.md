# Feature Specification: Phase 2 Foundational - コアインフラ構築

**Feature Branch**: `004-joseki-manager-phase2`
**Created**: 2026-01-16
**Status**: Draft
**Input**: Issue #18 - 全ユーザーストーリーが依存するコアインフラの構築（モデル、cshogi連携、ファクトリ）

## 概要

将棋定跡管理アプリケーション（Joseki Manager）の Phase 2 として、コアインフラストラクチャを構築する。
この Phase は全ユーザーストーリーの実装に必要な基盤を提供するため、完了するまで他の機能実装は開始できない。

設計ドキュメント（002-joseki-manager）に基づき、Django アプリケーション、データモデル、cshogi 連携、テストファクトリを実装する。

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Django アプリケーションの作成 (Priority: P1)

開発者は Django の `startapp` コマンドを使用して、定義されたアプリケーション（trees, labels, exports, core）と将棋ロジックモジュール（core/shogi/）を作成できる。

**Why this priority**: 他のすべてのモデルや機能の受け皿となるアプリケーション構造が必要。

**Independent Test**: 各アプリケーションディレクトリが存在し、Django アプリとして認識されることを確認。

**Acceptance Scenarios**:

1. **Given** Phase 1 が完了した状態、**When** `python manage.py startapp trees src/trees` を実行、**Then** trees アプリが作成される
2. **Given** 4つのアプリが作成された状態、**When** settings.py の INSTALLED_APPS を確認、**Then** 全アプリが登録されている
3. **Given** core/shogi/ ディレクトリが作成された状態、**When** `from src.core.shogi import position, rules` を実行、**Then** モジュールがインポートできる

---

### User Story 2 - データモデルの実装 (Priority: P1)

開発者は TDD アプローチでデータモデル（JosekiTree, Node, Edge, Label, NodeLabel）を実装できる。まずテストを書き、テストが失敗することを確認してから、モデルを実装してテストをパスさせる。

**Why this priority**: データモデルは全機能の基盤。API や機能はモデルなしには実装できない。

**Independent Test**: 各モデルのユニットテストがパスし、マイグレーションが正常に適用されることを確認。

**Acceptance Scenarios**:

1. **Given** テストファイルが存在しない状態、**When** JosekiTree のテストを作成して実行、**Then** テストが失敗する（Red フェーズ）
2. **Given** テストが失敗している状態、**When** JosekiTree モデルを実装、**Then** テストがパスする（Green フェーズ）
3. **Given** 全モデルが実装された状態、**When** `python manage.py makemigrations` を実行、**Then** マイグレーションファイルが生成される
4. **Given** マイグレーションファイルが存在する状態、**When** `python manage.py migrate` を実行、**Then** データベースにテーブルが作成される

---

### User Story 3 - cshogi 連携の実装 (Priority: P1)

開発者は cshogi ライブラリを使用して、SFEN 形式の局面処理と指し手の合法性検証を行うユーティリティ関数を実装できる。これらの関数は TDD で開発する。

**Why this priority**: 将棋のルール検証なしには、不正な手順が入力される可能性がある。データの整合性を保つための必須機能。

**Independent Test**: SFEN 処理と合法手検証のユニットテストがパスすることを確認。

**Acceptance Scenarios**:

1. **Given** 初期局面の SFEN 文字列、**When** parse_sfen() を呼び出す、**Then** 有効な局面オブジェクトが返される
2. **Given** 初期局面、**When** 合法手「7g7f」を検証、**Then** True が返される
3. **Given** 初期局面、**When** 不正手「1a1b」を検証、**Then** False が返される
4. **Given** 二歩が発生する局面、**When** 歩を打つ手を検証、**Then** False が返される

---

### User Story 4 - テストファクトリの作成 (Priority: P2)

開発者は factory_boy を使用して、各モデル（JosekiTree, Node, Edge, Label）のファクトリを作成できる。これにより後続のテストでテストデータを簡単に生成できる。

**Why this priority**: ファクトリはテスト効率を向上させるが、モデル自体のテストには必須ではない。

**Independent Test**: 各ファクトリでオブジェクトを生成し、データベースに保存できることを確認。

**Acceptance Scenarios**:

1. **Given** JosekiTreeFactory が定義された状態、**When** `JosekiTreeFactory.create()` を実行、**Then** JosekiTree インスタンスがデータベースに作成される
2. **Given** NodeFactory が定義された状態、**When** `NodeFactory.create(tree=tree)` を実行、**Then** 指定ツリーに属する Node が作成される
3. **Given** EdgeFactory が定義された状態、**When** `EdgeFactory.create(parent=p, child=c)` を実行、**Then** 親子関係を持つ Edge が作成される

---

### Edge Cases

- SFEN 文字列が不正な形式の場合は？→ ValueError を発生させ、明確なエラーメッセージを表示
- マイグレーション適用時にデータベース接続エラーが発生した場合は？→ Django 標準のエラーハンドリングに委ねる
- Node の sfen フィールドが 200 文字を超える場合は？→ バリデーションエラー（実際の SFEN は最大でも 100 文字程度）
- Edge で parent_id と child_id が同じ値の場合は？→ CheckConstraint で禁止（自己参照禁止）
- Label の color が無効な HEX 形式の場合は？→ RegexValidator でバリデーションエラー

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST trees, labels, exports, core の4つの Django アプリケーションを作成する
- **FR-002**: System MUST src/core/shogi/ に position.py と rules.py を作成する
- **FR-003**: System MUST JosekiTree モデルを data-model.md の定義に従って実装する
- **FR-004**: System MUST Node モデルを data-model.md の定義に従って実装する（tree_id, sfen の複合ユニーク制約を含む）
- **FR-005**: System MUST Edge モデルを data-model.md の定義に従って実装する（parent_id, move_usi の複合ユニーク制約、自己参照禁止制約を含む）
- **FR-006**: System MUST Label モデルを data-model.md の定義に従って実装する（name のユニーク制約を含む）
- **FR-007**: System MUST NodeLabel モデルを data-model.md の定義に従って実装する（node_id, label_id の複合ユニーク制約を含む）
- **FR-008**: System MUST cshogi を使用して SFEN 形式の局面を解析・検証する関数を提供する
- **FR-009**: System MUST cshogi を使用して指し手の合法性を検証する関数を提供する（二歩、打ち歩詰め等を自動検出）
- **FR-010**: System MUST factory_boy を使用して各モデルのファクトリを提供する
- **FR-011**: System MUST 全モデルに対するユニットテストを提供する（TDD: テスト先行）
- **FR-012**: System MUST マイグレーションファイルを生成し、適用できる

### Key Entities

このフェーズで実装するエンティティ（詳細は data-model.md 参照）:

- **JosekiTree（定跡ツリー）**: ルートエンティティ。name, description, is_deleted, deleted_at を持つ
- **Node（ノード）**: 各局面を表す。tree_id, sfen, comment, evaluation, metadata を持つ
- **Edge（エッジ）**: 親子ノード間の指し手。parent_id, child_id, move_usi, move_japanese を持つ
- **Label（ラベル）**: 戦型タグ。name, color, description を持つ
- **NodeLabel（ノード-ラベル関連）**: 多対多の中間テーブル

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 4つの Django アプリケーション（trees, labels, exports, core）が作成され、INSTALLED_APPS に登録されている
- **SC-002**: src/core/shogi/ ディレクトリに position.py と rules.py が存在し、インポートできる
- **SC-003**: 5つのモデル（JosekiTree, Node, Edge, Label, NodeLabel）のユニットテストが存在し、全てパスする
- **SC-004**: マイグレーションファイルが生成され、`python manage.py migrate` が成功する
- **SC-005**: SFEN 解析テストと合法手検証テストが存在し、全てパスする
- **SC-006**: 4つのファクトリ（JosekiTree, Node, Edge, Label）が存在し、オブジェクト生成テストがパスする
- **SC-007**: `uv run pytest tests/unit/` が全てパスする

## Assumptions

- Phase 1（Issue #17）が完了しており、Django プロジェクト構造が存在する
- PostgreSQL がローカルで稼働している
- uv を使用した依存関係管理が設定済み
- cshogi ライブラリがインストール済み
- 開発者は TDD の基本を理解している

## Related Documents

- 設計ブランチ: `002-joseki-manager`
- [spec.md](../002-joseki-manager/spec.md) - 機能仕様（全体）
- [plan.md](../002-joseki-manager/plan.md) - 実装計画
- [data-model.md](../002-joseki-manager/data-model.md) - データモデル定義
- [tasks.md](../002-joseki-manager/tasks.md) - タスク一覧（T011〜T035）

## タスク一覧（Issue #18 より）

### Core Infrastructure
- [ ] T011 Create Django app `trees`
- [ ] T012 Create Django app `labels`
- [ ] T013 Create Django app `exports`
- [ ] T014 Create Django app `core`
- [ ] T015 Create src/core/shogi/ modules

### Base Models (TDD)
- [ ] T016 Write failing test for JosekiTree model
- [ ] T017 Write failing test for Node model
- [ ] T018 Write failing test for Edge model
- [ ] T019 Write failing test for Label model
- [ ] T020 Write failing test for NodeLabel model
- [ ] T021 Implement JosekiTree model (make T016 pass)
- [ ] T022 Implement Node model (make T017 pass)
- [ ] T023 Implement Edge model (make T018 pass)
- [ ] T024 Implement Label model (make T019 pass)
- [ ] T025 Implement NodeLabel model (make T020 pass)
- [ ] T026 Create initial migrations
- [ ] T027 Apply migrations

### cshogi Integration (TDD)
- [ ] T028 Write failing test for SFEN handling
- [ ] T029 Write failing test for move validation
- [ ] T030 Implement SFEN utilities (make T028 pass)
- [ ] T031 Implement move validator (make T029 pass)

### Factory Setup
- [ ] T032 Create JosekiTreeFactory
- [ ] T033 Create NodeFactory
- [ ] T034 Create EdgeFactory
- [ ] T035 Create LabelFactory
