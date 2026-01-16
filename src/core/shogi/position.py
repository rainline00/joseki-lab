"""
局面処理モジュール

SFEN 形式の局面文字列を解析・正規化する機能を提供
"""

from typing import TYPE_CHECKING

import cshogi

from .exceptions import SfenParseError

if TYPE_CHECKING:
    from cshogi import Board

# 平手初期局面の SFEN（手数なし）
INITIAL_SFEN = "lnsgkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL b -"


def parse_sfen(sfen: str) -> "Board":
    """
    SFEN 文字列から cshogi.Board オブジェクトを生成する。

    Args:
        sfen: SFEN 形式の局面文字列（手数あり/なし両対応）

    Returns:
        cshogi.Board: 初期化された盤面オブジェクト

    Raises:
        SfenParseError: SFEN が無効な形式の場合
    """
    if not sfen or not sfen.strip():
        raise SfenParseError("空の SFEN は無効です", sfen=sfen)

    try:
        board = cshogi.Board(sfen)
        return board
    except Exception as e:
        raise SfenParseError(f"無効な SFEN 形式です: {e}", sfen=sfen) from e


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
    parts = sfen.strip().split()

    # SFEN は 盤面/手番/持ち駒[/手数] の形式
    # 最低3パーツ（盤面、手番、持ち駒）が必要
    if len(parts) < 3:
        raise SfenParseError(f"SFEN のパーツが不足しています: {sfen}", sfen=sfen)

    # 最初の3パーツのみを結合して返す（手数を除去）
    return " ".join(parts[:3])


def get_initial_sfen() -> str:
    """
    平手初期局面の SFEN を返す（手数なし）。

    Returns:
        str: "lnsgkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL b -"
    """
    return INITIAL_SFEN
