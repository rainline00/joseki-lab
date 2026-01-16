# Implementation Plan: Phase 2 - コアインフラ構築

**Branch**: `004-joseki-manager-phase2` | **Date**: 2026-01-16 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/004-joseki-manager-phase2/spec.md`

## Summary

将棋定跡管理アプリケーション（Joseki Manager）の Phase 2 として、全ユーザーストーリーが依存するコアインフラストラクチャを構築する。Django アプリケーション（trees, labels, exports, core）、データモデル（JosekiTree, Node, Edge, Label, NodeLabel）、cshogi 連携（SFEN 処理、合法手検証）、テストファクトリを TDD で実装する。

## Technical Context

**Language/Version**: Python 3.11+
**Primary Dependencies**: Django 5.0+, Django REST Framework 3.14+, cshogi 0.8+
**Storage**: PostgreSQL 15+
**Testing**: pytest, pytest-django, factory_boy, PostgreSQL（CD-001）
**Target Platform**: Linux/macOS/Windows（ローカルサーバー）
**Project Type**: Single project（REST API バックエンド）
**Performance Goals**: YAGNI - 目標設定なし（ボトルネック発見時に最適化）
**Constraints**: シングルユーザー、認証なし、ローカル実行
**Scale/Scope**: 定跡ツリー数十個、ノード数千〜数万規模

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| 原則 | 状態 | 対応 |
|------|------|------|
| I. 日本語ドキュメンテーション | ✅ Pass | すべての技術文書を日本語で作成 |
| II. シンプルさ優先 | ✅ Pass | 最小限の実装から開始、不要な機能なし |
| III. 明確なコミュニケーション | ✅ Pass | カスタム例外で明確なエラーメッセージ（CD-002） |
| IV. ブランチ運用ポリシー | ✅ Pass | `004-joseki-manager-phase2` ブランチで作業 |
| V. テスト駆動開発（TDD） | ✅ Pass | Red-Green-Refactor サイクルを徹底 |

**判定**: すべてのゲートをパス。

---

## Project Structure

### Documentation (this feature)

```text
specs/004-joseki-manager-phase2/
├── plan.md              # This file
├── spec.md              # Feature specification
├── research.md          # Phase 0: Technical research
├── data-model.md        # Phase 1: Entity definitions (updated with CD-003/004/005)
├── quickstart.md        # Phase 1: Development setup guide
├── contracts/           # Phase 1: Internal interfaces
│   └── interfaces.md    # Module interface definitions
├── checklists/          # Quality checklists
│   └── requirements.md  # Specification checklist
└── tasks.md             # Phase 2 output (/speckit.tasks で生成)
```

### Source Code (repository root)

```text
src/
├── joseki/                    # Django project (Phase 1 で作成済み)
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── trees/                     # 定跡ツリー管理アプリ [Phase 2]
│   ├── __init__.py
│   ├── apps.py
│   ├── models.py              # JosekiTree, Node, Edge
│   ├── admin.py
│   └── migrations/
├── labels/                    # ラベル管理アプリ [Phase 2]
│   ├── __init__.py
│   ├── apps.py
│   ├── models.py              # Label, NodeLabel
│   ├── admin.py
│   └── migrations/
├── exports/                   # エクスポート機能アプリ [Phase 2 - 空]
│   ├── __init__.py
│   └── apps.py
└── core/                      # 共通機能 [Phase 2]
    ├── __init__.py
    ├── apps.py
    └── shogi/                 # 将棋ロジックラッパー
        ├── __init__.py
        ├── position.py        # SFEN handling
        ├── rules.py           # Move validation
        └── exceptions.py      # Custom exceptions (CD-002)

tests/
├── conftest.py                # pytest fixtures (Phase 1 で作成済み)
├── factories.py               # factory_boy factories [Phase 2]
└── unit/
    ├── test_models.py         # Model tests [Phase 2]
    ├── test_position.py       # SFEN handling tests [Phase 2]
    └── test_rules.py          # Move validation tests [Phase 2]
```

**Structure Decision**: Phase 1 で構築された基本構造を継承。モデルは trees/labels アプリに配置し、cshogi 連携は core/shogi/ に集約。

---

## Complexity Tracking

> **該当なし**: Constitution Check に違反がないため、複雑さの正当化は不要。

---

## Design Decisions

### 1. SFEN 形式と手数管理（CD-003, CD-004）

**決定**: 手数なし SFEN + `ply` フィールド + `sfen_with_ply` property

**理由**:
- 局面の一意識別には手数は不要（同一盤面は同一ノード）
- 手数情報は定跡学習や棋譜表示で必要なため、`ply` フィールドで別途管理
- cshogi は手数なし SFEN を正常に読み取れることを検証済み
- 表示用途で手数あり SFEN が必要な場合は `sfen_with_ply` property を使用

### 2. エラーハンドリング（CD-002）

**決定**: カスタム例外でラップして raise

**理由**:
- cshogi のエラーを Python 例外にラップすることで、呼び出し元で柔軟に処理可能
- デバッグが容易（エラー発生箇所と原因が明確）
- 例外階層: ShogiError > SfenParseError, InvalidMoveError > IllegalMoveError

### 3. テスト戦略（CD-001）

**決定**: PostgreSQL（Docker 使用）でテスト実行

**理由**:
- 本番環境との一貫性を保証
- JSONB・CHECK 制約など PostgreSQL 固有機能のテストが可能
- docker-compose.test.yml で簡単にセットアップ可能

### 4. Edge.move_japanese（CD-005）

**決定**: NULLABLE（後から生成可能）

**理由**:
- 日本語表記は表示用途のため、move_usi から後で生成可能
- データ入力の簡略化と柔軟性を優先
- cshogi の機能で必要に応じて生成

---

## Implementation Phases

### Phase 2.1: Django アプリケーション作成

1. `trees` アプリを作成し、INSTALLED_APPS に登録
2. `labels` アプリを作成し、INSTALLED_APPS に登録
3. `exports` アプリを作成し、INSTALLED_APPS に登録
4. `core` アプリを作成し、INSTALLED_APPS に登録
5. `core/shogi/` モジュール構造を作成

### Phase 2.2: データモデル実装（TDD）

1. **Red**: JosekiTree のテストを作成（失敗を確認）
2. **Green**: JosekiTree モデルを実装（テストパス）
3. **Red**: Node のテストを作成（ply, sfen_with_ply を含む）
4. **Green**: Node モデルを実装
5. **Red**: Edge のテストを作成（自己参照禁止を含む）
6. **Green**: Edge モデルを実装
7. **Red**: Label のテストを作成
8. **Green**: Label モデルを実装
9. **Red**: NodeLabel のテストを作成
10. **Green**: NodeLabel モデルを実装
11. マイグレーションファイルを生成・適用

### Phase 2.3: cshogi 連携実装（TDD）

1. **Red**: SFEN 処理のテストを作成
   - parse_sfen: 正常系・異常系
   - normalize_sfen: 手数除去
2. **Green**: position.py を実装
3. **Red**: 合法手検証のテストを作成
   - is_legal_move: 正常手・不正手
   - validate_move: 例外発生
4. **Green**: rules.py を実装
5. exceptions.py を作成（カスタム例外）

### Phase 2.4: テストファクトリ作成

1. JosekiTreeFactory を作成
2. NodeFactory を作成
3. EdgeFactory を作成
4. LabelFactory を作成
5. ファクトリを使用したテストを作成・実行

---

## Success Criteria

Phase 2 の完了条件（spec.md より）:

- [ ] SC-001: 4つの Django アプリケーション（trees, labels, exports, core）が作成され、INSTALLED_APPS に登録されている
- [ ] SC-002: src/core/shogi/ ディレクトリに position.py と rules.py が存在し、インポートできる
- [ ] SC-003: 5つのモデル（JosekiTree, Node, Edge, Label, NodeLabel）のユニットテストが存在し、全てパスする
- [ ] SC-004: マイグレーションファイルが生成され、`python manage.py migrate` が成功する
- [ ] SC-005: SFEN 解析テストと合法手検証テストが存在し、全てパスする
- [ ] SC-006: 4つのファクトリ（JosekiTree, Node, Edge, Label）が存在し、オブジェクト生成テストがパスする
- [ ] SC-007: `uv run pytest tests/unit/` が全てパスする

---

## Next Steps

1. `/speckit.tasks` - タスク一覧を生成（tasks.md）
2. `/speckit.implement` - 実装を開始

---

## References

- [spec.md](./spec.md) - Phase 2 仕様書
- [research.md](./research.md) - 技術調査
- [data-model.md](./data-model.md) - データモデル定義
- [quickstart.md](./quickstart.md) - 開発環境セットアップ
- [contracts/interfaces.md](./contracts/interfaces.md) - 内部インターフェース定義
- [002-joseki-manager/plan.md](../002-joseki-manager/plan.md) - 全体実装計画
