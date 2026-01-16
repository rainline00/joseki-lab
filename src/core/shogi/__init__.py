"""
将棋ロジックラッパーモジュール

cshogi ライブラリをラップし、SFEN 処理と合法手検証機能を提供する
"""

from .exceptions import (
    IllegalMoveError,
    InvalidMoveError,
    SfenParseError,
    ShogiError,
)
from .position import get_initial_sfen, normalize_sfen, parse_sfen
from .rules import apply_move, get_legal_moves, is_legal_move, validate_move

__all__ = [
    # exceptions
    "ShogiError",
    "SfenParseError",
    "InvalidMoveError",
    "IllegalMoveError",
    # position
    "parse_sfen",
    "normalize_sfen",
    "get_initial_sfen",
    # rules
    "is_legal_move",
    "validate_move",
    "get_legal_moves",
    "apply_move",
]
