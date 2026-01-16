"""
Factory Boy factories for Joseki Manager tests.

テスト用のモデルファクトリを定義
"""

import factory

from labels.models import Label, NodeLabel
from trees.models import Edge, JosekiTree, Node

# 平手初期局面の SFEN（手数なし）
INITIAL_SFEN = "lnsgkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL b -"


class BaseFactory(factory.django.DjangoModelFactory):
    """
    基底ファクトリクラス

    すべてのモデルファクトリはこのクラスを継承する
    """

    class Meta:
        abstract = True


class JosekiTreeFactory(BaseFactory):
    """
    JosekiTree ファクトリ

    Attributes:
        name: 自動生成される一意の名前
        description: デフォルト空文字
        is_deleted: デフォルト False
    """

    class Meta:
        model = JosekiTree

    name = factory.Sequence(lambda n: f"定跡ツリー {n}")
    description = factory.Faker("text", max_nb_chars=200, locale="ja_JP")


class NodeFactory(BaseFactory):
    """
    Node ファクトリ

    Attributes:
        tree: 自動生成される JosekiTree
        sfen: 平手初期局面のデフォルト SFEN
        ply: デフォルト 0
    """

    class Meta:
        model = Node

    tree = factory.SubFactory(JosekiTreeFactory)
    sfen = factory.Sequence(lambda n: f"{INITIAL_SFEN[:-1]}{n % 10}")  # 各ノードでユニークなSFEN
    ply = 0
    comment = ""
    evaluation = None


class RootNodeFactory(NodeFactory):
    """
    ルートノード（初期局面）ファクトリ

    実際の初期局面 SFEN を持つノードを生成
    """

    sfen = INITIAL_SFEN
    ply = 0


class EdgeFactory(BaseFactory):
    """
    Edge ファクトリ

    Attributes:
        parent: 自動生成される Node
        child: 自動生成される Node（同一ツリー）
        move_usi: デフォルト "7g7f"
    """

    class Meta:
        model = Edge

    parent = factory.SubFactory(NodeFactory)
    child = factory.LazyAttribute(
        lambda obj: NodeFactory(tree=obj.parent.tree, ply=obj.parent.ply + 1)
    )
    move_usi = factory.Sequence(lambda n: f"7g{7 - (n % 5)}f")  # ユニークな指し手
    move_japanese = ""


class LabelFactory(BaseFactory):
    """
    Label ファクトリ

    Attributes:
        name: 自動生成される一意の名前
        color: デフォルト "#FF0000"
    """

    class Meta:
        model = Label

    name = factory.Sequence(lambda n: f"ラベル {n}")
    color = "#FF0000"
    description = ""


class NodeLabelFactory(BaseFactory):
    """
    NodeLabel ファクトリ

    Attributes:
        node: 自動生成される Node
        label: 自動生成される Label
    """

    class Meta:
        model = NodeLabel

    node = factory.SubFactory(NodeFactory)
    label = factory.SubFactory(LabelFactory)
