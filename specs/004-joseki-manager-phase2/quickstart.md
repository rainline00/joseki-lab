# Quickstart: Phase 2 - コアインフラ構築

**Feature**: 004-joseki-manager-phase2
**Date**: 2026-01-16

## 前提条件

Phase 1（003-joseki-manager-phase1）が完了していること。以下が設定済み：

- Django プロジェクト構造（src/joseki/）
- uv による依存関係管理（pyproject.toml）
- pytest/pytest-django の基本設定

## 開発環境セットアップ

### 1. PostgreSQL テスト環境の準備（CD-001）

Phase 2 ではテストに PostgreSQL を使用します。

```bash
# Docker Compose で PostgreSQL を起動
docker compose -f docker-compose.test.yml up -d

# または既存の PostgreSQL を使用
# .env ファイルで DATABASE_URL を設定
```

### 2. 依存関係の同期

```bash
uv sync
```

### 3. テストの実行

```bash
# 全テスト実行
uv run pytest

# 特定のテストファイル
uv run pytest tests/unit/test_models.py

# TDD: テストを監視モードで実行
uv run pytest --watch
```

---

## Django アプリケーション作成

Phase 2 で作成するアプリケーション：

```bash
# trees アプリ
uv run python src/manage.py startapp trees src/trees

# labels アプリ
uv run python src/manage.py startapp labels src/labels

# exports アプリ
uv run python src/manage.py startapp exports src/exports

# core アプリ
uv run python src/manage.py startapp core src/core
```

### shogi モジュールの作成

```bash
# core/shogi/ ディレクトリを作成
mkdir -p src/core/shogi

# 必要なファイルを作成
touch src/core/shogi/__init__.py
touch src/core/shogi/position.py
touch src/core/shogi/rules.py
touch src/core/shogi/exceptions.py
```

---

## TDD ワークフロー

### Red-Green-Refactor サイクル

1. **Red**: 失敗するテストを書く

```python
# tests/unit/test_models.py
import pytest
from src.trees.models import JosekiTree

@pytest.mark.django_db
class TestJosekiTree:
    def test_create_tree(self):
        tree = JosekiTree.objects.create(name="矢倉")
        assert tree.name == "矢倉"
        assert tree.is_deleted is False
```

2. **Green**: テストを通過する最小限の実装

```python
# src/trees/models.py
import uuid
from django.db import models

class JosekiTree(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    is_deleted = models.BooleanField(default=False)
    # ... 他のフィールド
```

3. **Refactor**: コード品質の改善

---

## cshogi 連携

### SFEN 処理（CD-003, CD-004）

```python
# src/core/shogi/position.py
import cshogi
from .exceptions import SfenParseError

def parse_sfen(sfen: str) -> cshogi.Board:
    """SFEN 文字列から Board オブジェクトを生成"""
    try:
        return cshogi.Board(sfen)
    except Exception as e:
        raise SfenParseError(sfen, str(e))

def normalize_sfen(sfen: str) -> str:
    """転置検出用に SFEN を正規化（手数を除去）"""
    parts = sfen.split(' ')
    return ' '.join(parts[:3])  # 盤面, 手番, 持ち駒のみ
```

### 合法手検証

```python
# src/core/shogi/rules.py
import cshogi
from .exceptions import InvalidMoveError, IllegalMoveError

def is_legal_move(sfen: str, move_usi: str) -> bool:
    """指し手が合法かどうかを検証"""
    board = cshogi.Board(sfen)
    try:
        move = board.move_from_usi(move_usi)
        return board.is_legal(move)
    except Exception:
        return False

def validate_move(sfen: str, move_usi: str) -> None:
    """指し手を検証し、不正なら例外を発生"""
    if not is_legal_move(sfen, move_usi):
        raise IllegalMoveError(move_usi, f"Illegal move from {sfen}")
```

---

## カスタム例外（CD-002）

```python
# src/core/shogi/exceptions.py

class ShogiError(Exception):
    """将棋関連エラーの基底クラス"""
    pass

class SfenParseError(ShogiError):
    """SFEN 解析エラー"""
    def __init__(self, sfen: str, message: str = None):
        self.sfen = sfen
        super().__init__(message or f"Invalid SFEN: {sfen}")

class InvalidMoveError(ShogiError):
    """不正な指し手エラー"""
    def __init__(self, move: str, reason: str = None):
        self.move = move
        super().__init__(reason or f"Invalid move: {move}")

class IllegalMoveError(InvalidMoveError):
    """合法でない指し手（二歩、打ち歩詰めなど）"""
    pass
```

---

## マイグレーション

```bash
# マイグレーションファイルを生成
uv run python src/manage.py makemigrations trees labels

# マイグレーションを適用
uv run python src/manage.py migrate
```

---

## Factory Boy ファクトリ

```python
# tests/factories.py
import factory
from src.trees.models import JosekiTree, Node, Edge
from src.labels.models import Label

class JosekiTreeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = JosekiTree

    name = factory.Sequence(lambda n: f"定跡ツリー {n}")
    description = ""
    is_deleted = False

class NodeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Node

    tree = factory.SubFactory(JosekiTreeFactory)
    sfen = "lnsgkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL b -"
    ply = 0

class EdgeFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Edge

    parent = factory.SubFactory(NodeFactory)
    child = factory.SubFactory(NodeFactory)
    move_usi = "7g7f"

class LabelFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Label

    name = factory.Sequence(lambda n: f"ラベル {n}")
    color = "#FF0000"
```

---

## 参照

- [spec.md](./spec.md) - Phase 2 仕様書
- [data-model.md](./data-model.md) - データモデル定義
- [research.md](./research.md) - 技術調査
- [002-joseki-manager/quickstart.md](../002-joseki-manager/quickstart.md) - 全体クイックスタート
