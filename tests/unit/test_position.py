"""
Position tests for cshogi integration.

SFEN 解析、正規化、初期局面取得のテスト
"""

import pytest


class TestParseSfen:
    """parse_sfen 関数のテスト"""

    def test_parse_initial_position(self):
        """初期局面の SFEN を解析できる"""
        from core.shogi.position import parse_sfen

        sfen = "lnsgkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL b -"
        board = parse_sfen(sfen)

        assert board is not None
        assert board.move_number == 0

    def test_parse_sfen_with_ply(self):
        """手数付き SFEN を解析できる"""
        from core.shogi.position import parse_sfen

        sfen = "lnsgkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL b - 1"
        board = parse_sfen(sfen)

        assert board is not None

    def test_parse_sfen_after_move(self):
        """手を進めた後の SFEN を解析できる"""
        from core.shogi.position import parse_sfen

        # 7六歩を指した後の局面
        sfen = "lnsgkgsnl/1r5b1/ppppppppp/9/9/2P6/PP1PPPPPP/1B5R1/LNSGKGSNL w -"
        board = parse_sfen(sfen)

        assert board is not None

    def test_parse_invalid_sfen(self):
        """無効な SFEN はエラーになる"""
        from core.shogi.exceptions import SfenParseError
        from core.shogi.position import parse_sfen

        with pytest.raises(SfenParseError) as exc_info:
            parse_sfen("invalid sfen string")

        assert exc_info.value.sfen == "invalid sfen string"

    def test_parse_empty_sfen(self):
        """空の SFEN はエラーになる"""
        from core.shogi.exceptions import SfenParseError
        from core.shogi.position import parse_sfen

        with pytest.raises(SfenParseError):
            parse_sfen("")


class TestNormalizeSfen:
    """normalize_sfen 関数のテスト"""

    def test_normalize_sfen_removes_ply(self):
        """SFEN から手数を除去する"""
        from core.shogi.position import normalize_sfen

        sfen_with_ply = "lnsgkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL b - 1"
        normalized = normalize_sfen(sfen_with_ply)

        assert normalized == "lnsgkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL b -"

    def test_normalize_sfen_without_ply(self):
        """手数なし SFEN はそのまま返す"""
        from core.shogi.position import normalize_sfen

        sfen = "lnsgkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL b -"
        normalized = normalize_sfen(sfen)

        assert normalized == sfen

    def test_normalize_sfen_with_hand_pieces(self):
        """持ち駒がある SFEN を正規化できる"""
        from core.shogi.position import normalize_sfen

        sfen_with_ply = "lnsgkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL b P2p 10"
        normalized = normalize_sfen(sfen_with_ply)

        assert normalized == "lnsgkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL b P2p"

    def test_normalize_sfen_insufficient_parts(self):
        """パーツが不足している SFEN はエラーになる"""
        from core.shogi.exceptions import SfenParseError
        from core.shogi.position import normalize_sfen

        with pytest.raises(SfenParseError):
            normalize_sfen("lnsgkgsnl/1r5b1/ppppppppp b")


class TestGetInitialSfen:
    """get_initial_sfen 関数のテスト"""

    def test_get_initial_sfen(self):
        """平手初期局面の SFEN を取得できる"""
        from core.shogi.position import get_initial_sfen

        initial = get_initial_sfen()

        assert initial == "lnsgkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL b -"

    def test_initial_sfen_has_no_ply(self):
        """初期局面 SFEN には手数がない"""
        from core.shogi.position import get_initial_sfen

        initial = get_initial_sfen()
        parts = initial.split()

        # 3パーツのみ（盤面、手番、持ち駒）
        assert len(parts) == 3

    def test_initial_sfen_is_valid(self):
        """初期局面 SFEN は有効な形式"""
        from core.shogi.position import get_initial_sfen, parse_sfen

        initial = get_initial_sfen()
        board = parse_sfen(initial)

        assert board is not None
