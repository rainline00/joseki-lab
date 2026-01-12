# 設計レポート: 将棋定跡管理アプリケーション（Joseki Manager）

**ブランチ**: `002-joseki-manager`
**作成日**: 2026-01-12
**ステータス**: 設計完了、実装準備完了

## 概要

このブランチでは、将棋の序盤定跡を木構造（DAG）形式で管理する REST API バックエンドの設計を行いました。

## 成果物一覧

| ファイル | 内容 | 状態 |
|----------|------|------|
| [spec.md](./spec.md) | 機能仕様（5 User Stories、17 FRs） | ✅ 完了 |
| [plan.md](./plan.md) | 実装計画（技術スタック、プロジェクト構造） | ✅ 完了 |
| [data-model.md](./data-model.md) | データモデル（5 エンティティ、Django モデル定義） | ✅ 完了 |
| [contracts/openapi.yaml](./contracts/openapi.yaml) | API 仕様（23 エンドポイント） | ✅ 完了 |
| [research.md](./research.md) | 技術調査（cshogi、Django ツリー構造） | ✅ 完了 |
| [quickstart.md](./quickstart.md) | 開発環境セットアップガイド | ✅ 完了 |
| [tasks.md](./tasks.md) | 実装タスク一覧（140 タスク、9 フェーズ） | ✅ 完了 |
| [checklists/requirements.md](./checklists/requirements.md) | 仕様品質チェックリスト | ✅ 完了 |

## 技術選定

| 項目 | 選定 | 理由 |
|------|------|------|
| 言語 | Python 3.11+ | 型ヒント、パフォーマンス向上 |
| フレームワーク | Django 5.0+ / DRF 3.14+ | 堅牢な ORM、REST API サポート |
| 将棋ライブラリ | cshogi 0.8+ | Cython 実装で高速、KIF/KI2 パーサー内蔵 |
| データベース | PostgreSQL 15+ | JSONB サポート、堅牢性 |
| テスト | pytest / pytest-django / factory_boy | TDD サポート |

## User Stories

| ID | タイトル | Priority | 関連 FR |
|----|----------|----------|---------|
| US1 | 定跡ツリーの作成と手順入力 | P1 (MVP) | FR-001〜004, 007, 008, 012, 013 |
| US2 | 戦型ラベルの付与と管理 | P1 | FR-005, 006 |
| US3 | 定跡ツリーの視覚的表示と操作 | P2 | FR-007, 008 |
| US4 | 定跡データのインポート・エクスポート | P2 | FR-009, 010, 014, 015 |
| US5 | コメント・メモの追加 | P3 | FR-011 |

## Clarification Sessions

### Session 1 (2026-01-12)
- 定跡ツリー間の関係性 → 基本独立、マージ機能あり
- 削除時のデータ保護 → ゴミ箱に移動、復元可能
- 初期リリースの提供形態 → REST API のみ
- ユーザー管理と認証 → シングルユーザー、認証なし
- エクスポート形式 → JSON + KIF

### Session 2 (2026-01-12 Pre-tasks)
- 千日手の扱い → 検出せず通常のノードとして登録
- 自動削除期間 → 30日
- 転置ノード削除 → エッジのみ削除（ノードは残る）
- API 応答時間の測定条件 → PostgreSQL ウォーム、単一リクエスト
- コメント全文検索 → スコープ外

## 実装フェーズ

| Phase | 内容 | タスク数 | GitHub Issue |
|-------|------|----------|--------------|
| Phase 1 | Setup - プロジェクト初期化 | 10 | [#17](https://github.com/rainline00/joseki-lab/issues/17) |
| Phase 2 | Foundational - コアインフラ | 25 | [#18](https://github.com/rainline00/joseki-lab/issues/18) |
| Phase 3 | US1 - 定跡ツリー作成 (MVP) | 24 | [#19](https://github.com/rainline00/joseki-lab/issues/19) |
| Phase 4 | US2 - ラベル管理 | 21 | 後続作成 |
| Phase 5 | US3 - 視覚表示データ | 9 | 後続作成 |
| Phase 6 | US4 - インポート/エクスポート | 23 | 後続作成 |
| Phase 7 | US5 - コメント | 7 | 後続作成 |
| Phase 8 | Trash & Recovery | 11 | 後続作成 |
| Phase 9 | Polish | 10 | 後続作成 |

**追跡 Issue**: [#20](https://github.com/rainline00/joseki-lab/issues/20) - Phase 4-9 の Issue 作成

## ブランチ戦略

```
002-joseki-manager          ← 設計用ブランチ（このブランチ）
    │
    ├── 002-joseki-manager-phase1  ← Phase 1 実装
    │       ↓ PR to develop
    │
    ├── 002-joseki-manager-phase2  ← Phase 2 実装
    │       ↓ PR to develop
    │
    └── 002-joseki-manager-phase3  ← Phase 3 実装 (MVP)
            ↓ PR to develop
```

各 Phase は独立した feature ブランチで実装し、小さな PR を作成します。

## Constitution 適合性

| 原則 | 状態 |
|------|------|
| I. 日本語ドキュメンテーション | ✅ Pass |
| II. シンプルさ優先 | ✅ Pass |
| III. 明確なコミュニケーション | ✅ Pass |
| IV. ブランチ運用ポリシー | ✅ Pass |
| V. テスト駆動開発（TDD） | ✅ Pass（tasks.md で徹底） |

## 品質メトリクス

| 指標 | 値 |
|------|-----|
| Total Functional Requirements | 17 |
| Total User Stories | 5 |
| Total Tasks | 140 |
| FR Coverage | 100% |
| API Endpoints | 23 |
| Data Model Entities | 5 |
| Critical Issues | 0 |

## 次のステップ

1. この PR をマージして設計をベースラインとして確定
2. Issue #17 (Phase 1) から実装開始
3. 各 Phase で feature ブランチを作成し、必要に応じて speckit ワークフローを再実行
4. MVP (Phase 3) 完了後、Issue #20 を参照して残りの Phase の Issue を作成

## 参考資料

- [cshogi GitHub](https://github.com/TadaoYamaoka/cshogi)
- [Django REST Framework](https://www.django-rest-framework.org/)
- [SFEN 形式仕様](http://hgm.nubati.net/variants/shogi.txt)
