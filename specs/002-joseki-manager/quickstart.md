# Quickstart: 将棋定跡管理アプリケーション開発環境

**Feature**: 002-joseki-manager
**Date**: 2026-01-12

## 前提条件

- Python 3.11以上
- PostgreSQL 15以上
- Git

## セットアップ手順

### 1. リポジトリのクローン

```bash
git clone <repository-url>
cd joseki-lab
git checkout 002-joseki-manager
```

### 2. Python仮想環境の作成

```bash
# venv を使用
python3.11 -m venv .venv
source .venv/bin/activate  # Linux/macOS
# または
.venv\Scripts\activate  # Windows

# pip のアップグレード
pip install --upgrade pip
```

### 3. 依存パッケージのインストール

```bash
# 開発用依存関係を含めてインストール
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

**requirements.txt** (作成予定):
```
Django>=5.0,<6.0
djangorestframework>=3.14,<4.0
django-filter>=24.0,<25.0
psycopg[binary]>=3.1,<4.0
cshogi>=0.8,<1.0
drf-spectacular>=0.27,<1.0
```

**requirements-dev.txt** (作成予定):
```
pytest>=8.0,<9.0
pytest-django>=4.8,<5.0
pytest-cov>=4.1,<5.0
factory-boy>=3.3,<4.0
black>=24.0
ruff>=0.2
mypy>=1.8
django-stubs>=4.2
djangorestframework-stubs>=3.14
```

### 4. PostgreSQL データベースの準備

```bash
# PostgreSQL にログイン
psql -U postgres

# データベースとユーザーを作成
CREATE USER joseki WITH PASSWORD 'joseki_dev_password';
CREATE DATABASE joseki_db OWNER joseki;
GRANT ALL PRIVILEGES ON DATABASE joseki_db TO joseki;
\q
```

### 5. 環境変数の設定

`.env` ファイルを作成:

```bash
# .env
DEBUG=True
SECRET_KEY=your-secret-key-for-development-only
DATABASE_URL=postgres://joseki:joseki_dev_password@localhost:5432/joseki_db
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 6. Django プロジェクトの初期化

```bash
cd src

# マイグレーション
python manage.py migrate

# スーパーユーザー作成（任意）
python manage.py createsuperuser

# 開発サーバー起動
python manage.py runserver
```

### 7. 動作確認

```bash
# ヘルスチェック
curl http://localhost:8000/api/v1/health/

# OpenAPI スキーマ取得
curl http://localhost:8000/api/v1/schema/
```

---

## 開発コマンド

### テスト実行

```bash
# 全テスト実行
pytest

# カバレッジ付き
pytest --cov=src --cov-report=html

# 特定のテストファイル
pytest tests/unit/test_models.py

# マーカー指定
pytest -m "not slow"
```

### コード品質チェック

```bash
# フォーマット
black src/ tests/

# リンター
ruff check src/ tests/

# 型チェック
mypy src/
```

### マイグレーション

```bash
# マイグレーション作成
python manage.py makemigrations

# マイグレーション適用
python manage.py migrate

# マイグレーション状態確認
python manage.py showmigrations
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
│   └── 002-joseki-manager/  # この機能のドキュメント
├── requirements.txt
├── requirements-dev.txt
├── pyproject.toml
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

### cshogi のインストールエラー

```bash
# Cython が必要な場合
pip install cython
pip install cshogi
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
python manage.py migrate trees zero
python manage.py migrate
```

---

## 次のステップ

1. `/speckit.tasks` でタスク一覧を生成
2. タスクに従って TDD で実装開始
3. 各タスク完了後にテストがパスすることを確認
