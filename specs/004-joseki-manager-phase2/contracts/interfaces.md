# Internal Interfaces: Phase 2 - コアインフラ構築

**Feature**: 004-joseki-manager-phase2
**Date**: 2026-01-16
**Status**: Draft

## 概要

Phase 2 は REST API ではなく、コアインフラストラクチャ（モデル、cshogi 連携、テストファクトリ）を構築するフェーズです。
このドキュメントでは、内部モジュールのインターフェースを定義します。

---

## 1. cshogi 連携モジュール（src/core/shogi/）

### position.py - 局面処理

```python
def parse_sfen(sfen: str) -> cshogi.Board:
    """
    SFEN 文字列から cshogi.Board オブジェクトを生成する。

    Args:
        sfen: SFEN 形式の局面文字列（手数あり/なし両対応）

    Returns:
        cshogi.Board: 初期化された盤面オブジェクト

    Raises:
        SfenParseError: SFEN が無効な形式の場合
    """

def normalize_sfen(sfen: str) -> str:
    """
    転置検出用に SFEN を正規化する（手数を除去）。

    Args:
        sfen: SFEN 形式の局面文字列

    Returns:
        str: 手数を除いた正規化 SFEN（盤面 + 手番 + 持ち駒）

    Example:
        >>> normalize_sfen("lnsgkgsnl/.../LNSGKGSNL b - 1")
        "lnsgkgsnl/.../LNSGKGSNL b -"
    """

def get_initial_sfen() -> str:
    """
    平手初期局面の SFEN を返す（手数なし）。

    Returns:
        str: "lnsgkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL b -"
    """
```

### rules.py - ルール検証

```python
def is_legal_move(sfen: str, move_usi: str) -> bool:
    """
    指し手が合法かどうかを検証する。

    Args:
        sfen: 現在の局面（SFEN 形式）
        move_usi: 検証する指し手（USI 形式、例: "7g7f"）

    Returns:
        bool: 合法なら True、不正なら False
    """

def validate_move(sfen: str, move_usi: str) -> None:
    """
    指し手を検証し、不正なら例外を発生させる。

    Args:
        sfen: 現在の局面（SFEN 形式）
        move_usi: 検証する指し手（USI 形式）

    Raises:
        InvalidMoveError: 指し手の形式が無効な場合
        IllegalMoveError: 合法でない指し手の場合（二歩、打ち歩詰めなど）
    """

def get_legal_moves(sfen: str) -> list[str]:
    """
    現在の局面から可能な全ての合法手を取得する。

    Args:
        sfen: 現在の局面（SFEN 形式）

    Returns:
        list[str]: USI 形式の合法手リスト

    Raises:
        SfenParseError: SFEN が無効な形式の場合
    """

def apply_move(sfen: str, move_usi: str) -> str:
    """
    局面に指し手を適用し、新しい局面の SFEN を返す。

    Args:
        sfen: 現在の局面（SFEN 形式、手数なし）
        move_usi: 適用する指し手（USI 形式）

    Returns:
        str: 新しい局面の SFEN（手数なし）

    Raises:
        InvalidMoveError: 指し手の形式が無効な場合
        IllegalMoveError: 合法でない指し手の場合
    """
```

### exceptions.py - 例外クラス

```python
class ShogiError(Exception):
    """将棋関連エラーの基底クラス"""
    pass

class SfenParseError(ShogiError):
    """SFEN 解析エラー"""
    sfen: str  # 無効な SFEN 文字列

class InvalidMoveError(ShogiError):
    """不正な指し手エラー（形式が無効）"""
    move: str  # 無効な指し手

class IllegalMoveError(InvalidMoveError):
    """合法でない指し手エラー（ルール違反）"""
    pass
```

---

## 2. モデルインターフェース

### JosekiTree

```python
class JosekiTree(models.Model):
    # Properties
    @property
    def root_node(self) -> "Node | None":
        """ルートノード（初期局面のノード）を返す"""

    # Methods
    def soft_delete(self) -> None:
        """ソフトデリート（is_deleted=True, deleted_at=now）"""

    def restore(self) -> None:
        """ソフトデリートを解除"""
```

### Node

```python
class Node(models.Model):
    # Properties
    @property
    def is_root(self) -> bool:
        """ルートノードかどうか"""

    @property
    def sfen_with_ply(self) -> str:
        """手数を含む SFEN を返す（CD-004）"""

    # Methods
    def get_children(self) -> QuerySet["Edge"]:
        """子ノードへのエッジを取得"""

    def get_parents(self) -> QuerySet["Edge"]:
        """親ノードからのエッジを取得（転置対応）"""
```

### Edge

```python
class Edge(models.Model):
    # Validation
    def clean(self) -> None:
        """
        Raises:
            ValidationError: parent と child が同じノードの場合
            ValidationError: parent と child が異なるツリーの場合
        """
```

---

## 3. テストファクトリインターフェース

```python
# tests/factories.py

class JosekiTreeFactory(DjangoModelFactory):
    """
    Attributes:
        name: 自動生成される一意の名前
        description: デフォルト空文字
        is_deleted: デフォルト False
    """

class NodeFactory(DjangoModelFactory):
    """
    Attributes:
        tree: 自動生成される JosekiTree
        sfen: 平手初期局面のデフォルト SFEN
        ply: デフォルト 0
    """

class EdgeFactory(DjangoModelFactory):
    """
    Attributes:
        parent: 自動生成される Node
        child: 自動生成される Node（同一ツリー）
        move_usi: デフォルト "7g7f"
    """

class LabelFactory(DjangoModelFactory):
    """
    Attributes:
        name: 自動生成される一意の名前
        color: デフォルト "#FF0000"
    """
```

---

## 4. 使用例

### モデル作成とファクトリ使用

```python
# ファクトリを使用したテストデータ作成
tree = JosekiTreeFactory(name="矢倉定跡")
root_node = NodeFactory(tree=tree, sfen=get_initial_sfen(), ply=0)

# 手を進める
new_sfen = apply_move(root_node.sfen, "7g7f")
child_node = NodeFactory(tree=tree, sfen=new_sfen, ply=1)
edge = EdgeFactory(parent=root_node, child=child_node, move_usi="7g7f")

# sfen_with_ply プロパティの使用
assert child_node.sfen_with_ply == f"{new_sfen} 1"
```

### cshogi 連携

```python
from src.core.shogi.position import parse_sfen, normalize_sfen
from src.core.shogi.rules import is_legal_move, validate_move
from src.core.shogi.exceptions import IllegalMoveError

# SFEN 解析
board = parse_sfen("lnsgkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL b -")

# 合法手チェック
assert is_legal_move("lnsgkgsnl/.../LNSGKGSNL b -", "7g7f") == True
assert is_legal_move("lnsgkgsnl/.../LNSGKGSNL b -", "1a1b") == False

# 検証と例外
try:
    validate_move(sfen, "invalid_move")
except IllegalMoveError as e:
    print(f"不正な手: {e.move}")
```

---

## 参照

- [data-model.md](./data-model.md) - データモデル定義
- [research.md](./research.md) - 技術調査（cshogi 使用例）
- [spec.md](./spec.md) - Phase 2 仕様書
