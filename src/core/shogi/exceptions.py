"""
将棋関連の例外クラス

cshogi のエラーを Python 例外にラップし、呼び出し元で柔軟に処理可能にする
"""


class ShogiError(Exception):
    """将棋関連エラーの基底クラス"""

    pass


class SfenParseError(ShogiError):
    """SFEN 解析エラー

    Attributes:
        sfen: 無効な SFEN 文字列
    """

    def __init__(self, message: str, sfen: str = ""):
        super().__init__(message)
        self.sfen = sfen


class InvalidMoveError(ShogiError):
    """不正な指し手エラー（形式が無効）

    Attributes:
        move: 無効な指し手
    """

    def __init__(self, message: str, move: str = ""):
        super().__init__(message)
        self.move = move


class IllegalMoveError(InvalidMoveError):
    """合法でない指し手エラー（ルール違反）

    二歩、打ち歩詰め、行き所のない駒など、将棋のルールに違反する手
    """

    pass
