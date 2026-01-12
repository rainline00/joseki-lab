<!--
Sync Impact Report:
- Version change: N/A → 1.0.0
- Added principles:
  - I. 日本語ドキュメンテーション (Japanese Documentation)
  - II. シンプルさ優先 (Simplicity First)
  - III. 明確なコミュニケーション (Clear Communication)
- Templates requiring updates: ✅ Reviewed (no updates needed for initial constitution)
-->

# Joseki Lab Constitution

## Core Principles

### I. 日本語ドキュメンテーション

すべての技術文書は日本語で記述することを原則とする。

- CLAUDE.md、README.md、その他のドキュメントファイルは日本語で作成すること
- コード内のコメントは日本語を推奨（英語も可）
- コミットメッセージは日本語または英語のいずれかで統一すること
- 変数名・関数名・クラス名はプログラミングの慣例に従い英語を使用

### II. シンプルさ優先

複雑さを避け、シンプルな解決策を優先する。

- YAGNI（You Aren't Gonna Need It）の原則に従う
- 必要最小限の機能から始め、必要に応じて拡張する
- 過度な抽象化を避け、明確で直接的なコードを書く

### III. 明確なコミュニケーション

コードとドキュメントは明確で理解しやすいものにする。

- 自己説明的なコードを書く
- 必要に応じて適切なコメントを追加する
- エラーメッセージは具体的で対処方法がわかるものにする

## 開発ワークフロー

### コードレビュー

- すべての変更はプルリクエストを通じて行う
- レビューコメントは建設的で具体的に

### テスト

- 重要な機能にはテストを書くことを推奨
- テストは読みやすく、メンテナンスしやすいものに

## Governance

- この Constitution はプロジェクトの基本方針として全メンバーが遵守する
- 変更が必要な場合は、Issue を作成して議論した上で修正する
- バージョンはセマンティックバージョニングに従う
  - MAJOR: 原則の削除や大幅な変更
  - MINOR: 新しい原則やセクションの追加
  - PATCH: 文言の修正や明確化

**Version**: 1.0.0 | **Ratified**: 2026-01-12 | **Last Amended**: 2026-01-12
