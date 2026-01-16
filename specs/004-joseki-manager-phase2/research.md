# Technical Research: Phase 2 - コアインフラ構築

**Feature**: 004-joseki-manager-phase2
**Date**: 2026-01-16
**Status**: Complete

## 1. 調査項目一覧

Phase 2 の明確化プロセス（/speckit.clarify）で以下の項目が決定済み。追加調査は不要。

| # | 調査項目 | 決定 | 根拠 |
|---|----------|------|------|
| CD-001 | テスト用データベース | PostgreSQL（Docker使用） | 本番環境との一貫性 |
| CD-002 | cshogi エラーハンドリング | カスタム例外でラップ | 呼び出し元での柔軟な処理 |
| CD-003 | SFEN 形式と手数管理 | 手数なし SFEN + ply フィールド | 局面一意識別と手数管理の分離 |
| CD-004 | SFEN 出力方法 | sfen_with_ply property | 表示用途で手数あり SFEN が必要 |
| CD-005 | Edge.move_japanese 必須性 | NULLABLE | move_usi から後で生成可能 |

---

## 2. cshogi SFEN 検証結果

明確化プロセスで実施した検証結果を記録。

### 検証コード

```python
import cshogi

# 手数なし SFEN の読み取りテスト
sfen_without_ply = "lnsgkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL b -"
board = cshogi.Board(sfen_without_ply)

# 結果
# - 読み取り: 成功
# - 内部手数: 0 (move_number)
# - 出力 SFEN: "lnsgkgsnl/...b - 0"
```

### 結論

- cshogi は手数なし SFEN を正常に読み取れる
- 内部では `move_number = 0` として扱われる
- データベースには手数なし SFEN を保存し、`ply` フィールドで手数を管理する

---

## 3. Django モデル設計の確認

### 002-joseki-manager からの継承

data-model.md で定義されたモデル設計を継承。Phase 2 の明確化で以下を追加。

#### Node モデルへの追加フィールド

```python
class Node(models.Model):
    # ... 既存フィールド ...
    ply = models.IntegerField(default=0, help_text='手数（0=初期局面）')

    @property
    def sfen_with_ply(self) -> str:
        """手数を含む SFEN を返す"""
        return f"{self.sfen} {self.ply}"
```

#### Edge モデルの変更

```python
class Edge(models.Model):
    # ... 既存フィールド ...
    move_japanese = models.CharField(max_length=20, blank=True)  # NULLABLE に変更
```

---

## 4. テスト戦略

### PostgreSQL テスト環境（CD-001）

```yaml
# docker-compose.test.yml
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: test
      POSTGRES_PASSWORD: test
      POSTGRES_DB: test_joseki
    ports:
      - "5433:5432"
```

```ini
# pytest.ini または pyproject.toml
[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "joseki.settings"
python_files = ["test_*.py"]
```

### TDD サイクル

1. **Red**: 失敗するテストを先に書く
2. **Green**: テストを通過する最小限の実装
3. **Refactor**: コード品質の改善

---

## 5. カスタム例外設計（CD-002）

### 例外階層

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

## 6. 参照ドキュメント

### 設計ドキュメント（002-joseki-manager）

- [spec.md](../002-joseki-manager/spec.md) - 全体仕様
- [plan.md](../002-joseki-manager/plan.md) - 実装計画
- [data-model.md](../002-joseki-manager/data-model.md) - データモデル定義
- [research.md](../002-joseki-manager/research.md) - 技術調査

### Phase 1（003-joseki-manager-phase1）

- [spec.md](../003-joseki-manager-phase1/spec.md) - プロジェクト初期化仕様

---

## 7. 結論

Phase 2 に必要な技術調査は 002-joseki-manager の research.md で完了しており、
Phase 2 固有の決定事項は明確化プロセス（CD-001〜CD-005）で解決済み。

**追加調査不要。Phase 1: Design に進行可能。**
