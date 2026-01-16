# Quickstart: 将棋定跡管理アプリケーション開発環境（uv 版）

**Feature**: 003-joseki-manager-phase1
**Date**: 2026-01-14

## 前提条件

- Python 3.11以上
- PostgreSQL 15以上
- Git
- [uv](https://github.com/astral-sh/uv)（Python パッケージマネージャー）

### uv のインストール

```bash
# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# pipx 経由
pipx install uv
```

## セットアップ手順

### 1. リポジトリのクローン

```bash
git clone <repository-url>
cd joseki-lab
git checkout 003-joseki-manager-phase1
```

### 2. 依存パッケージのインストール

```bash
# uv sync で依存関係を自動インストール
# .venv が自動的に作成される
uv sync
```

これで以下がインストールされます:

**本番依存関係**:
- Django 5.0+
- Django REST Framework 3.14+
- django-filter 24.0+
- psycopg[binary] 3.1+
- cshogi 0.8+
- drf-spectacular 0.27+

**開発用依存関係**:
- pytest 8.0+
- pytest-django 4.8+
- pytest-cov 4.1+
- factory-boy 3.3+
- black 24.0+
- ruff 0.2+
- mypy 1.8+
- django-stubs 4.2+
- djangorestframework-stubs 3.14+

### 3. PostgreSQL データベースの準備

```bash
# PostgreSQL にログイン
psql -U postgres

# データベースとユーザーを作成
CREATE USER joseki WITH PASSWORD 'joseki_dev_password';
CREATE DATABASE joseki_db OWNER joseki;
GRANT ALL PRIVILEGES ON DATABASE joseki_db TO joseki;
\q
```

### 4. 環境変数の設定

`.env` ファイルを作成（`.env.example` からコピー）:

```bash
cp .env.example .env
```

`.env` ファイルを編集:

```bash
# .env
DEBUG=True
SECRET_KEY=your-secret-key-for-development-only
DATABASE_URL=postgres://joseki:joseki_dev_password@localhost:5432/joseki_db
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 5. Django プロジェクトの初期化

```bash
# マイグレーション
uv run python src/manage.py migrate

# スーパーユーザー作成（任意）
uv run python src/manage.py createsuperuser

# 開発サーバー起動
uv run python src/manage.py runserver
```

### 6. 動作確認

```bash
# Django システムチェック
uv run python src/manage.py check

# OpenAPI スキーマ取得（サーバー起動後）
curl http://localhost:8000/api/schema/

# Swagger UI でドキュメント閲覧
# http://localhost:8000/api/docs/

# Redoc でドキュメント閲覧
# http://localhost:8000/api/redoc/
```

---

## 開発コマンド

### テスト実行

```bash
# 全テスト実行
uv run pytest

# カバレッジ付き
uv run pytest --cov=src --cov-report=html

# 特定のテストファイル
uv run pytest tests/unit/test_models.py

# マーカー指定
uv run pytest -m "not slow"

# テスト収集のみ（環境確認用）
uv run pytest --collect-only
```

### コード品質チェック

```bash
# フォーマット
uv run black src/ tests/

# リンター
uv run ruff check src/ tests/

# リンター（自動修正）
uv run ruff check --fix src/ tests/

# 型チェック
uv run mypy src/
```

### 依存関係管理

```bash
# 新しい依存関係を追加
uv add <package-name>

# 開発用依存関係を追加
uv add --dev <package-name>

# 依存関係の更新
uv lock --upgrade

# 依存関係の同期
uv sync
```

### マイグレーション

```bash
# マイグレーション作成
uv run python src/manage.py makemigrations

# マイグレーション適用
uv run python src/manage.py migrate

# マイグレーション状態確認
uv run python src/manage.py showmigrations
```

---

## プロジェクト構成

```
joseki-lab/
├── src/
│   ├── joseki/              # Django プロジェクト設定
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── trees/               # 定跡ツリーアプリ
│   ├── labels/              # ラベルアプリ
│   ├── exports/             # エクスポートアプリ
│   ├── core/                # 共通機能
│   └── manage.py
├── tests/
│   ├── conftest.py
│   ├── factories.py
│   ├── unit/
│   ├── integration/
│   └── contract/
├── specs/
│   ├── 002-joseki-manager/  # 設計ドキュメント
│   └── 003-joseki-manager-phase1/  # Phase 1 ドキュメント
├── pyproject.toml           # 依存関係とツール設定
├── uv.lock                  # ロックファイル
├── .env.example
└── README.md
```

---

## TDD ワークフロー

Constitution V（テスト駆動開発）に従い、以下のサイクルで開発:

### 1. Red - 失敗するテストを書く

```python
# tests/unit/test_models.py
def test_create_joseki_tree():
    """定跡ツリーを作成できること"""
    tree = JosekiTree.objects.create(name="矢倉")

    assert tree.id is not None
    assert tree.name == "矢倉"
    assert tree.is_deleted is False
```

### 2. Green - テストを通す最小限のコードを実装

```python
# src/trees/models.py
class JosekiTree(models.Model):
    name = models.CharField(max_length=200)
    is_deleted = models.BooleanField(default=False)
```

### 3. Refactor - リファクタリング

```python
# 必要に応じてコードを改善
# テストは常にパスすること
```

---

## API テスト

### cURL での動作確認

```bash
# ツリー作成
curl -X POST http://localhost:8000/api/v1/trees/ \
  -H "Content-Type: application/json" \
  -d '{"name": "矢倉", "description": "矢倉囲いの定跡"}'

# ツリー一覧
curl http://localhost:8000/api/v1/trees/

# 指し手追加
curl -X POST http://localhost:8000/api/v1/trees/{tree_id}/nodes/{node_id}/moves/ \
  -H "Content-Type: application/json" \
  -d '{"move_usi": "7g7f"}'
```

### pytest での API テスト

```python
# tests/integration/test_api.py
import pytest
from rest_framework.test import APIClient

@pytest.fixture
def api_client():
    return APIClient()

def test_create_tree(api_client, db):
    """API経由で定跡ツリーを作成できること"""
    response = api_client.post('/api/v1/trees/', {
        'name': '四間飛車',
        'description': 'ノーマル四間飛車の定跡'
    })

    assert response.status_code == 201
    assert response.data['name'] == '四間飛車'
```

---

## cshogi の使用例

### 基本操作

```python
import cshogi

# 初期局面の作成
board = cshogi.Board()

# SFEN 取得
sfen = board.sfen()
# 'lnsgkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL b - 1'

# 指し手の実行
board.push_usi('7g7f')

# 合法手チェック
move = cshogi.move_from_usi('2g2f')
if board.is_legal(move):
    board.push(move)
```

### KIF ファイルの解析

```python
import cshogi.KIF

# KIF ファイルを読み込み
for kif in cshogi.KIF.Parser.parse_file('game.kif'):
    print(f"先手: {kif.names[0]}")
    print(f"後手: {kif.names[1]}")

    # 指し手を順に適用
    board = cshogi.Board()
    for move_usi in kif.moves:
        board.push_usi(move_usi)
        print(f"{move_usi} -> {board.sfen()}")
```

---

## トラブルシューティング

### uv がインストールされていない

```bash
# uv のインストール
curl -LsSf https://astral.sh/uv/install.sh | sh

# パスを通す（必要な場合）
export PATH="$HOME/.cargo/bin:$PATH"
```

### cshogi のインストールエラー

```bash
# Cython が必要な場合
uv add cython
uv sync
```

### PostgreSQL 接続エラー

```bash
# PostgreSQL サービスの状態確認
sudo systemctl status postgresql  # Linux
brew services list | grep postgresql  # macOS

# 接続テスト
psql -U joseki -d joseki_db -h localhost
```

### マイグレーションエラー

```bash
# マイグレーションをリセット（開発環境のみ）
uv run python src/manage.py migrate trees zero
uv run python src/manage.py migrate
```

### uv.lock の競合

```bash
# ロックファイルを再生成
uv lock --upgrade
uv sync
```

---

## 次のステップ

1. `/speckit.tasks` でタスク一覧を生成
2. タスクに従って TDD で実装開始
3. 各タスク完了後にテストがパスすることを確認
4. PR を `develop` へ作成
