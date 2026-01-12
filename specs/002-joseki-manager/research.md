# Technical Research: 将棋定跡管理アプリケーション

**Feature**: 002-joseki-manager
**Date**: 2026-01-12
**Status**: Complete

## 1. 将棋ライブラリ比較

### 調査対象

| ライブラリ | 実装 | パフォーマンス | メンテナンス |
|-----------|------|---------------|-------------|
| cshogi | Cython | 高速 | アクティブ |
| python-shogi | Pure Python | 低速 | 低頻度 |

### 決定: cshogi

**理由**:
- Cython実装による高パフォーマンス（大量棋譜処理に有利）
- KIF/KI2パーサー内蔵
- 合法手検証で二歩・打ち歩詰めを自動除外
- SFEN形式を完全サポート
- 機械学習向け機能あり（将来のAI評価値対応に有利）

**代替案として検討**:
- python-shogi: Pure Python実装のため遅い。KI2サポートが限定的。

### cshogi 基本使用例

```python
import cshogi

# 盤面作成
board = cshogi.Board()

# SFEN から盤面を初期化
board = cshogi.Board('lnsgkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL b - 1')

# 指し手の実行（USI形式）
move = board.push_usi('7g7f')

# SFEN の取得（局面の一意識別子として使用）
sfen = board.sfen()

# 合法手の列挙（二歩・打ち歩詰めは自動除外）
for move in board.legal_moves:
    print(cshogi.move_to_usi(move))

# 合法性チェック
is_valid = board.is_legal(move)

# 王手・詰みチェック
is_check = board.is_check()
is_mate = board.is_mate()

# 千日手チェック
draw_status = board.is_draw()
```

### KIF/KI2 ファイル解析

```python
import cshogi.KIF
import cshogi.KI2

# KIF ファイルの解析
for kif in cshogi.KIF.Parser.parse_file('game.kif'):
    print(kif.names)    # 対局者名
    print(kif.moves)    # 指し手リスト（USI形式）
    print(kif.sfen)     # 初期局面 SFEN

# KI2 ファイルの解析
for ki2 in cshogi.KI2.Parser.parse_file('game.ki2'):
    print(ki2.moves)

# エンコーディング注意
# .kif 拡張子: Shift-JIS (cp932)
# .kifu 拡張子: UTF-8
```

---

## 2. Django ツリー構造

### 調査対象

| パッケージ | アルゴリズム | 読取速度 | 書込速度 | 転置対応 |
|-----------|------------|---------|---------|---------|
| django-mptt | Nested Set | 非常に速い | 遅い | ❌ |
| django-treebeard | Materialized Path | 速い | 中程度 | ❌ |
| 隣接リスト | Foreign Key | 中程度 | 速い | ✅（Edgeテーブル追加） |

### 決定: 隣接リスト + エッジテーブル

**理由**:
- 転置（同一局面への複数経路）をサポートする必要がある
- django-mptt/treebeardは純粋な木構造のみ対応
- 1000ノード規模ならシンプルな隣接リストで十分な性能
- 実装がシンプルで理解しやすい

**代替案として検討**:
- django-mptt: 読み取りは高速だが、書き込みが遅く転置に対応できない
- django-treebeard: MPTTより堅牢だが、やはり転置に対応できない

### DAG構造の実装パターン

```python
from django.db import models

class Node(models.Model):
    """ノード - 局面を表す"""
    tree = models.ForeignKey('JosekiTree', on_delete=models.CASCADE)
    sfen = models.CharField(max_length=200, db_index=True)
    comment = models.TextField(blank=True)

    class Meta:
        unique_together = ['tree', 'sfen']  # 同一ツリー内で局面は一意

class Edge(models.Model):
    """エッジ - 親子関係（指し手）を表す"""
    parent = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='child_edges')
    child = models.ForeignKey(Node, on_delete=models.CASCADE, related_name='parent_edges')
    move_usi = models.CharField(max_length=10)

    class Meta:
        unique_together = ['parent', 'move_usi']  # 同じ親から同じ手は1回のみ
```

**この設計の利点**:
- 転置対応: 同一ノードに複数のエッジが接続可能
- クエリ効率: `prefetch_related` で N+1 問題を回避可能
- シンプル: Django標準機能のみで実装可能

---

## 3. Django REST Framework ベストプラクティス

### 再帰的シリアライザ

```python
from rest_framework import serializers

class NodeSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Node
        fields = ('id', 'sfen', 'move_usi', 'comment', 'labels', 'children')

    def get_children(self, obj):
        # エッジ経由で子ノードを取得
        child_edges = obj.child_edges.select_related('child')
        children = []
        for edge in child_edges:
            child_data = NodeSerializer(edge.child, context=self.context).data
            child_data['move_from_parent'] = edge.move_usi
            children.append(child_data)
        return children
```

### パフォーマンス最適化

```python
from django.db.models import Prefetch

class NodeViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        return Node.objects.prefetch_related(
            Prefetch('child_edges', queryset=Edge.objects.select_related('child')),
            'node_labels__label'
        )
```

### 深さ制限付きシリアライザ

```python
class NodeSerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    def __init__(self, *args, **kwargs):
        self.max_depth = kwargs.pop('max_depth', 3)
        self.current_depth = kwargs.pop('current_depth', 0)
        super().__init__(*args, **kwargs)

    def get_children(self, obj):
        if self.current_depth >= self.max_depth:
            return []  # 深さ制限に達したら子を展開しない

        child_edges = obj.child_edges.select_related('child')
        return [
            NodeSerializer(
                edge.child,
                max_depth=self.max_depth,
                current_depth=self.current_depth + 1,
                context=self.context
            ).data
            for edge in child_edges
        ]
```

---

## 4. SFEN形式について

### 形式説明

SFEN（Shogi Forsyth-Edwards Notation）は局面を文字列で表現する標準形式。

```
lnsgkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL b - 1
└─────────────────盤面─────────────────┘ │ │ └手数
                                        │ └持ち駒
                                        └手番(b:先手, w:後手)
```

### 盤面の駒表記

| 記号 | 駒 | 成駒 |
|------|-----|------|
| P/p | 歩 | +P/+p |
| L/l | 香 | +L/+l |
| N/n | 桂 | +N/+n |
| S/s | 銀 | +S/+s |
| G/g | 金 | - |
| B/b | 角 | +B/+b |
| R/r | 飛 | +R/+r |
| K/k | 玉 | - |

大文字=先手、小文字=後手

### 転置検出における注意

```python
def normalize_sfen(sfen: str) -> str:
    """転置検出用にSFENを正規化"""
    parts = sfen.split(' ')
    # 手数（4番目）は転置判定に含めない
    # 同一盤面・同一手番・同一持ち駒なら同一局面
    return ' '.join(parts[:3])
```

---

## 5. KIF/KI2形式について

### KIF形式

```
# ---- Kifu for Windows V7 棋譜ファイル ----
開始日時：2024/01/15 19:00:00
先手：羽生善治
後手：藤井聡太
手合割：平手
   1 ７六歩(77)
   2 ３四歩(34)
   3 ２六歩(27)
```

### KI2形式（簡略形式）

```
先手：羽生善治
後手：藤井聡太
▲７六歩△３四歩▲２六歩
```

### エンコーディング

| 拡張子 | エンコーディング |
|--------|-----------------|
| .kif | Shift-JIS (cp932) |
| .kifu | UTF-8 |
| .ki2 | Shift-JIS (cp932) |

---

## 6. 参考資料

### ライブラリ

- [cshogi GitHub](https://github.com/TadaoYamaoka/cshogi)
- [cshogi Documentation](https://tadaoyamaoka.github.io/cshogi/)
- [python-shogi GitHub](https://github.com/gunyarakun/python-shogi)

### Django

- [Django REST Framework](https://www.django-rest-framework.org/)
- [django-mptt](https://django-mptt.readthedocs.io/)
- [django-treebeard](https://django-treebeard.readthedocs.io/)

### 将棋形式

- [SFEN形式仕様](http://hgm.nubati.net/variants/shogi.txt)
- [KIF形式仕様](https://gist.github.com/Marken-Foo/7694548af1f562ecd01fba6b60a9c96a)
