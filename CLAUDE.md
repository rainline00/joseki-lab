# CLAUDE.md

このファイルは Claude Code（claude.ai/code）がこのリポジトリで作業する際のガイダンスを提供します。

## プロジェクト概要

Joseki Lab は、Claude Code と speckit ワークフローを使用した開発プロジェクトです。

## ドキュメンテーション方針

### 日本語記述の原則

**すべての技術文書は日本語で記述すること。**

- このファイル（CLAUDE.md）を含むすべてのドキュメントは日本語で作成する
- README.md、その他の `.md` ファイルも日本語で記述
- コード内のコメントは日本語を推奨（英語も可）
- コミットメッセージは日本語または英語で統一

### 例外

- 変数名、関数名、クラス名などのコード識別子は英語を使用
- 外部ライブラリのドキュメント引用は原文のまま

## 開発ガイドライン

### コード品質

- シンプルで読みやすいコードを書く
- YAGNI の原則に従い、不要な機能は実装しない
- 自己説明的なコードを心がける

### Constitution

プロジェクトの基本方針は `.specify/memory/constitution.md` に定義されています。
開発時はこの方針に従ってください。

## speckit ワークフロー

このプロジェクトでは speckit を使用した機能開発ワークフローを採用しています。

- `/speckit.specify` - 機能仕様の作成
- `/speckit.plan` - 実装計画の作成
- `/speckit.tasks` - タスク一覧の生成
- `/speckit.implement` - 実装の実行

詳細は `.claude/commands/` ディレクトリ内のファイルを参照してください。

## Active Technologies
- Python 3.11+ + Django 5.0+, Django REST Framework 3.14+, cshogi 0.8+ (002-joseki-manager)
- PostgreSQL 15+ (002-joseki-manager)

## Recent Changes
- 002-joseki-manager: Added Python 3.11+ + Django 5.0+, Django REST Framework 3.14+, cshogi 0.8+
