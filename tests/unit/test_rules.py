"""
Rules tests for cshogi integration.

合法手検証、指し手適用のテスト
"""

import pytest


class TestIsLegalMove:
    """is_legal_move 関数のテスト"""

    def test_legal_move_7g7f(self):
        """7六歩は合法手"""
        from core.shogi.position import get_initial_sfen
        from core.shogi.rules import is_legal_move

        initial = get_initial_sfen()
        assert is_legal_move(initial, "7g7f") is True

    def test_legal_move_2g2f(self):
        """2六歩は合法手"""
        from core.shogi.position import get_initial_sfen
        from core.shogi.rules import is_legal_move

        initial = get_initial_sfen()
        assert is_legal_move(initial, "2g2f") is True

    def test_illegal_move_invalid_format(self):
        """無効な形式の指し手は不正"""
        from core.shogi.position import get_initial_sfen
        from core.shogi.rules import is_legal_move

        initial = get_initial_sfen()
        assert is_legal_move(initial, "invalid") is False

    def test_illegal_move_wrong_piece(self):
        """駒がない場所からの手は不正"""
        from core.shogi.position import get_initial_sfen
        from core.shogi.rules import is_legal_move

        initial = get_initial_sfen()
        assert is_legal_move(initial, "5e5f") is False

    def test_illegal_move_same_position(self):
        """同じ位置への手は不正"""
        from core.shogi.position import get_initial_sfen
        from core.shogi.rules import is_legal_move

        initial = get_initial_sfen()
        assert is_legal_move(initial, "7g7g") is False

    def test_is_legal_move_with_invalid_sfen(self):
        """無効な SFEN では False を返す"""
        from core.shogi.rules import is_legal_move

        assert is_legal_move("invalid sfen", "7g7f") is False


class TestValidateMove:
    """validate_move 関数のテスト"""

    def test_validate_legal_move(self):
        """合法手はエラーなし"""
        from core.shogi.position import get_initial_sfen
        from core.shogi.rules import validate_move

        initial = get_initial_sfen()
        # Should not raise
        validate_move(initial, "7g7f")

    def test_validate_invalid_move_format(self):
        """無効な形式の指し手は InvalidMoveError"""
        from core.shogi.exceptions import InvalidMoveError
        from core.shogi.position import get_initial_sfen
        from core.shogi.rules import validate_move

        initial = get_initial_sfen()
        with pytest.raises(InvalidMoveError) as exc_info:
            validate_move(initial, "invalid")

        assert exc_info.value.move == "invalid"

    def test_validate_illegal_move(self):
        """不正な指し手は InvalidMoveError（または IllegalMoveError）"""
        from core.shogi.exceptions import InvalidMoveError
        from core.shogi.position import get_initial_sfen
        from core.shogi.rules import validate_move

        initial = get_initial_sfen()
        # cshogi は駒がない場所からの手を InvalidMoveError として扱う
        with pytest.raises(InvalidMoveError) as exc_info:
            validate_move(initial, "5e5f")  # 駒がない場所からの手

        assert exc_info.value.move == "5e5f"

    def test_validate_move_with_invalid_sfen(self):
        """無効な SFEN では SfenParseError"""
        from core.shogi.exceptions import SfenParseError
        from core.shogi.rules import validate_move

        with pytest.raises(SfenParseError):
            validate_move("invalid sfen", "7g7f")


class TestGetLegalMoves:
    """get_legal_moves 関数のテスト"""

    def test_get_legal_moves_initial_position(self):
        """初期局面の合法手を取得できる"""
        from core.shogi.position import get_initial_sfen
        from core.shogi.rules import get_legal_moves

        initial = get_initial_sfen()
        moves = get_legal_moves(initial)

        assert isinstance(moves, list)
        assert len(moves) > 0
        assert "7g7f" in moves
        assert "2g2f" in moves

    def test_get_legal_moves_count(self):
        """初期局面の合法手は 30 手"""
        from core.shogi.position import get_initial_sfen
        from core.shogi.rules import get_legal_moves

        initial = get_initial_sfen()
        moves = get_legal_moves(initial)

        # 初期局面の合法手は 30 手
        assert len(moves) == 30

    def test_get_legal_moves_with_invalid_sfen(self):
        """無効な SFEN では SfenParseError"""
        from core.shogi.exceptions import SfenParseError
        from core.shogi.rules import get_legal_moves

        with pytest.raises(SfenParseError):
            get_legal_moves("invalid sfen")


class TestApplyMove:
    """apply_move 関数のテスト"""

    def test_apply_move_7g7f(self):
        """7六歩を適用できる"""
        from core.shogi.position import get_initial_sfen
        from core.shogi.rules import apply_move

        initial = get_initial_sfen()
        new_sfen = apply_move(initial, "7g7f")

        assert new_sfen is not None
        assert new_sfen != initial
        # 手番が変わっている
        assert "w -" in new_sfen or "w" in new_sfen.split()[1]

    def test_apply_move_returns_normalized_sfen(self):
        """apply_move は手数なし SFEN を返す"""
        from core.shogi.position import get_initial_sfen
        from core.shogi.rules import apply_move

        initial = get_initial_sfen()
        new_sfen = apply_move(initial, "7g7f")

        parts = new_sfen.split()
        # 3パーツのみ（盤面、手番、持ち駒）
        assert len(parts) == 3

    def test_apply_move_invalid_format(self):
        """無効な形式の指し手は InvalidMoveError"""
        from core.shogi.exceptions import InvalidMoveError
        from core.shogi.position import get_initial_sfen
        from core.shogi.rules import apply_move

        initial = get_initial_sfen()
        with pytest.raises(InvalidMoveError):
            apply_move(initial, "invalid")

    def test_apply_move_illegal_move(self):
        """不正な指し手は InvalidMoveError（または IllegalMoveError）"""
        from core.shogi.exceptions import InvalidMoveError
        from core.shogi.position import get_initial_sfen
        from core.shogi.rules import apply_move

        initial = get_initial_sfen()
        # cshogi は駒がない場所からの手を InvalidMoveError として扱う
        with pytest.raises(InvalidMoveError):
            apply_move(initial, "5e5f")  # 駒がない場所からの手

    def test_apply_move_with_invalid_sfen(self):
        """無効な SFEN では SfenParseError"""
        from core.shogi.exceptions import SfenParseError
        from core.shogi.rules import apply_move

        with pytest.raises(SfenParseError):
            apply_move("invalid sfen", "7g7f")

    def test_apply_move_sequence(self):
        """連続して手を適用できる"""
        from core.shogi.position import get_initial_sfen
        from core.shogi.rules import apply_move

        sfen = get_initial_sfen()
        sfen = apply_move(sfen, "7g7f")  # 7六歩
        sfen = apply_move(sfen, "3c3d")  # 3四歩
        sfen = apply_move(sfen, "2g2f")  # 2六歩

        assert sfen is not None
        # 手番が後手（先手が 3 手、後手が 1 手なので先手番）
        assert "w -" in sfen or "w" in sfen.split()[1]
