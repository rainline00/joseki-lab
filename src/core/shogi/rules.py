"""
ルール検証モジュール

指し手の合法性チェックと局面の更新機能を提供
"""

import cshogi

from .exceptions import IllegalMoveError, InvalidMoveError, SfenParseError
from .position import normalize_sfen, parse_sfen


def is_legal_move(sfen: str, move_usi: str) -> bool:
    """
    指し手が合法かどうかを検証する。

    Args:
        sfen: 現在の局面（SFEN 形式）
        move_usi: 検証する指し手（USI 形式、例: "7g7f"）

    Returns:
        bool: 合法なら True、不正なら False
    """
    try:
        board = parse_sfen(sfen)
        move = board.move_from_usi(move_usi)

        if move is None or move == 0:
            return False

        return board.is_legal(move)
    except SfenParseError:
        return False
    except Exception:
        return False


def validate_move(sfen: str, move_usi: str) -> None:
    """
    指し手を検証し、不正なら例外を発生させる。

    Args:
        sfen: 現在の局面（SFEN 形式）
        move_usi: 検証する指し手（USI 形式）

    Raises:
        SfenParseError: SFEN が無効な形式の場合
        InvalidMoveError: 指し手の形式が無効な場合
        IllegalMoveError: 合法でない指し手の場合（二歩、打ち歩詰めなど）
    """
    board = parse_sfen(sfen)

    move = board.move_from_usi(move_usi)
    if move is None or move == 0:
        raise InvalidMoveError(f"無効な指し手形式です: {move_usi}", move=move_usi)

    if not board.is_legal(move):
        raise IllegalMoveError(f"合法でない指し手です: {move_usi}", move=move_usi)


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
    board = parse_sfen(sfen)
    legal_moves = []

    for move in board.legal_moves:
        move_usi = cshogi.move_to_usi(move)
        legal_moves.append(move_usi)

    return legal_moves


def apply_move(sfen: str, move_usi: str) -> str:
    """
    局面に指し手を適用し、新しい局面の SFEN を返す。

    Args:
        sfen: 現在の局面（SFEN 形式、手数なし）
        move_usi: 適用する指し手（USI 形式）

    Returns:
        str: 新しい局面の SFEN（手数なし）

    Raises:
        SfenParseError: SFEN が無効な形式の場合
        InvalidMoveError: 指し手の形式が無効な場合
        IllegalMoveError: 合法でない指し手の場合
    """
    board = parse_sfen(sfen)

    move = board.move_from_usi(move_usi)
    if move is None or move == 0:
        raise InvalidMoveError(f"無効な指し手形式です: {move_usi}", move=move_usi)

    if not board.is_legal(move):
        raise IllegalMoveError(f"合法でない指し手です: {move_usi}", move=move_usi)

    board.push(move)

    # 新しい局面の SFEN を取得し、手数を除去して返す
    new_sfen = board.sfen()
    return normalize_sfen(new_sfen)
