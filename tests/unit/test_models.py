"""
Model tests for Joseki Manager.

TDD Red-Green-Refactor: このファイルのテストを先に書き、実装前に FAIL することを確認
"""

import uuid
from datetime import datetime

import pytest
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone


# =============================================================================
# T016: JosekiTree Model Tests
# =============================================================================
@pytest.mark.django_db
class TestJosekiTreeModel:
    """JosekiTree モデルのテスト"""

    def test_create_joseki_tree(self):
        """JosekiTree を作成できる"""
        from trees.models import JosekiTree

        tree = JosekiTree.objects.create(
            name="矢倉定跡",
            description="矢倉戦法の定跡集",
        )

        assert tree.id is not None
        assert isinstance(tree.id, uuid.UUID)
        assert tree.name == "矢倉定跡"
        assert tree.description == "矢倉戦法の定跡集"
        assert tree.is_deleted is False
        assert tree.deleted_at is None
        assert tree.created_at is not None
        assert tree.updated_at is not None

    def test_joseki_tree_soft_delete(self):
        """JosekiTree をソフトデリートできる"""
        from trees.models import JosekiTree

        tree = JosekiTree.objects.create(name="テスト定跡")
        tree.soft_delete()

        assert tree.is_deleted is True
        assert tree.deleted_at is not None
        assert isinstance(tree.deleted_at, datetime)

    def test_joseki_tree_restore(self):
        """ソフトデリートした JosekiTree を復元できる"""
        from trees.models import JosekiTree

        tree = JosekiTree.objects.create(name="テスト定跡")
        tree.soft_delete()
        tree.restore()

        assert tree.is_deleted is False
        assert tree.deleted_at is None

    def test_joseki_tree_str(self):
        """JosekiTree の文字列表現"""
        from trees.models import JosekiTree

        tree = JosekiTree(name="振り飛車定跡")
        assert str(tree) == "振り飛車定跡"

    def test_joseki_tree_db_table(self):
        """JosekiTree のテーブル名"""
        from trees.models import JosekiTree

        assert JosekiTree._meta.db_table == "joseki_trees"


# =============================================================================
# T017: Node Model Tests
# =============================================================================
@pytest.mark.django_db
class TestNodeModel:
    """Node モデルのテスト"""

    def test_create_node(self):
        """Node を作成できる"""
        from trees.models import JosekiTree, Node

        tree = JosekiTree.objects.create(name="テスト定跡")
        sfen = "lnsgkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL b -"

        node = Node.objects.create(
            tree=tree,
            sfen=sfen,
            ply=0,
            comment="初期局面",
            evaluation=0,
        )

        assert node.id is not None
        assert isinstance(node.id, uuid.UUID)
        assert node.tree == tree
        assert node.sfen == sfen
        assert node.ply == 0
        assert node.comment == "初期局面"
        assert node.evaluation == 0
        assert node.metadata == {}
        assert node.created_at is not None
        assert node.updated_at is not None

    def test_node_ply_default(self):
        """Node の ply フィールドのデフォルト値は 0"""
        from trees.models import JosekiTree, Node

        tree = JosekiTree.objects.create(name="テスト定跡")
        node = Node.objects.create(
            tree=tree,
            sfen="lnsgkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL b -",
        )

        assert node.ply == 0

    def test_node_sfen_with_ply_property(self):
        """Node.sfen_with_ply は手数を含む SFEN を返す（CD-004）"""
        from trees.models import JosekiTree, Node

        tree = JosekiTree.objects.create(name="テスト定跡")
        sfen = "lnsgkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL b -"

        node = Node.objects.create(tree=tree, sfen=sfen, ply=5)

        assert node.sfen_with_ply == f"{sfen} 5"

    def test_node_unique_per_tree_sfen(self):
        """同一ツリー内で同じ SFEN のノードは作成できない"""
        from trees.models import JosekiTree, Node

        tree = JosekiTree.objects.create(name="テスト定跡")
        sfen = "lnsgkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL b -"

        Node.objects.create(tree=tree, sfen=sfen)

        with pytest.raises(IntegrityError):
            Node.objects.create(tree=tree, sfen=sfen)

    def test_node_same_sfen_different_tree(self):
        """異なるツリーでは同じ SFEN のノードを作成できる"""
        from trees.models import JosekiTree, Node

        tree1 = JosekiTree.objects.create(name="定跡1")
        tree2 = JosekiTree.objects.create(name="定跡2")
        sfen = "lnsgkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL b -"

        node1 = Node.objects.create(tree=tree1, sfen=sfen)
        node2 = Node.objects.create(tree=tree2, sfen=sfen)

        assert node1.id != node2.id

    def test_node_is_root_property(self):
        """Node.is_root はルートノードなら True を返す"""
        from trees.models import Edge, JosekiTree, Node

        tree = JosekiTree.objects.create(name="テスト定跡")
        root = Node.objects.create(
            tree=tree,
            sfen="lnsgkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL b -",
        )
        child = Node.objects.create(
            tree=tree,
            sfen="lnsgkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL w -",
            ply=1,
        )
        Edge.objects.create(parent=root, child=child, move_usi="7g7f")

        assert root.is_root is True
        assert child.is_root is False

    def test_node_db_table(self):
        """Node のテーブル名"""
        from trees.models import Node

        assert Node._meta.db_table == "nodes"

    def test_node_str(self):
        """Node の文字列表現"""
        from trees.models import JosekiTree, Node

        tree = JosekiTree.objects.create(name="テスト")
        sfen = "lnsgkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL b -"
        node = Node.objects.create(tree=tree, sfen=sfen)

        assert "テスト" in str(node)


# =============================================================================
# T018: Edge Model Tests
# =============================================================================
@pytest.mark.django_db
class TestEdgeModel:
    """Edge モデルのテスト"""

    def test_create_edge(self):
        """Edge を作成できる"""
        from trees.models import Edge, JosekiTree, Node

        tree = JosekiTree.objects.create(name="テスト定跡")
        parent = Node.objects.create(
            tree=tree,
            sfen="lnsgkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL b -",
            ply=0,
        )
        child = Node.objects.create(
            tree=tree,
            sfen="lnsgkgsnl/1r5b1/ppppppppp/9/9/P/9/PPPPPPPP/1B5R1/LNSGKGSNL w -",
            ply=1,
        )

        edge = Edge.objects.create(
            parent=parent,
            child=child,
            move_usi="7g7f",
            move_japanese="７六歩",
        )

        assert edge.id is not None
        assert isinstance(edge.id, uuid.UUID)
        assert edge.parent == parent
        assert edge.child == child
        assert edge.move_usi == "7g7f"
        assert edge.move_japanese == "７六歩"
        assert edge.created_at is not None

    def test_edge_move_japanese_nullable(self):
        """Edge.move_japanese は NULLABLE（CD-005）"""
        from trees.models import Edge, JosekiTree, Node

        tree = JosekiTree.objects.create(name="テスト定跡")
        parent = Node.objects.create(
            tree=tree,
            sfen="lnsgkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL b -",
        )
        child = Node.objects.create(
            tree=tree,
            sfen="lnsgkgsnl/1r5b1/ppppppppp/9/9/P/9/PPPPPPPP/1B5R1/LNSGKGSNL w -",
            ply=1,
        )

        # move_japanese なしで作成できる
        edge = Edge.objects.create(
            parent=parent,
            child=child,
            move_usi="7g7f",
        )

        assert edge.move_japanese == ""

    def test_edge_unique_move_from_parent(self):
        """同一親から同じ指し手のエッジは作成できない"""
        from trees.models import Edge, JosekiTree, Node

        tree = JosekiTree.objects.create(name="テスト定跡")
        parent = Node.objects.create(
            tree=tree,
            sfen="lnsgkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL b -",
        )
        child1 = Node.objects.create(
            tree=tree,
            sfen="sfen1 b -",
            ply=1,
        )
        child2 = Node.objects.create(
            tree=tree,
            sfen="sfen2 b -",
            ply=1,
        )

        Edge.objects.create(parent=parent, child=child1, move_usi="7g7f")

        with pytest.raises(IntegrityError):
            Edge.objects.create(parent=parent, child=child2, move_usi="7g7f")

    def test_edge_no_self_reference(self):
        """自己参照エッジは作成できない"""
        from trees.models import Edge, JosekiTree, Node

        tree = JosekiTree.objects.create(name="テスト定跡")
        node = Node.objects.create(
            tree=tree,
            sfen="lnsgkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL b -",
        )

        with pytest.raises(IntegrityError):
            Edge.objects.create(parent=node, child=node, move_usi="7g7f")

    def test_edge_db_table(self):
        """Edge のテーブル名"""
        from trees.models import Edge

        assert Edge._meta.db_table == "edges"

    def test_edge_str(self):
        """Edge の文字列表現"""
        from trees.models import Edge, JosekiTree, Node

        tree = JosekiTree.objects.create(name="テスト")
        parent = Node.objects.create(
            tree=tree,
            sfen="sfen1 b -",
        )
        child = Node.objects.create(
            tree=tree,
            sfen="sfen2 b -",
            ply=1,
        )
        edge = Edge.objects.create(
            parent=parent,
            child=child,
            move_usi="7g7f",
            move_japanese="７六歩",
        )

        assert "7g7f" in str(edge)


# =============================================================================
# T019: Label Model Tests
# =============================================================================
@pytest.mark.django_db
class TestLabelModel:
    """Label モデルのテスト"""

    def test_create_label(self):
        """Label を作成できる"""
        from labels.models import Label

        label = Label.objects.create(
            name="急戦",
            color="#FF0000",
            description="急戦形の定跡",
        )

        assert label.id is not None
        assert isinstance(label.id, uuid.UUID)
        assert label.name == "急戦"
        assert label.color == "#FF0000"
        assert label.description == "急戦形の定跡"
        assert label.created_at is not None

    def test_label_name_unique(self):
        """Label.name はユニーク"""
        from labels.models import Label

        Label.objects.create(name="急戦")

        with pytest.raises(IntegrityError):
            Label.objects.create(name="急戦")

    def test_label_color_nullable(self):
        """Label.color は NULLABLE"""
        from labels.models import Label

        label = Label.objects.create(name="持久戦")
        assert label.color == ""

    def test_label_color_hex_validation(self):
        """Label.color は HEX 形式（#RRGGBB）で検証"""
        from labels.models import Label

        label = Label(name="テスト", color="invalid")
        with pytest.raises(ValidationError):
            label.full_clean()

    def test_label_color_valid_hex(self):
        """Label.color は有効な HEX 形式を受け入れる"""
        from labels.models import Label

        label = Label(name="テスト", color="#AABBCC")
        label.full_clean()  # Should not raise

    def test_label_db_table(self):
        """Label のテーブル名"""
        from labels.models import Label

        assert Label._meta.db_table == "labels"

    def test_label_str(self):
        """Label の文字列表現"""
        from labels.models import Label

        label = Label(name="相掛かり")
        assert str(label) == "相掛かり"


# =============================================================================
# T020: NodeLabel Model Tests
# =============================================================================
@pytest.mark.django_db
class TestNodeLabelModel:
    """NodeLabel モデルのテスト"""

    def test_create_node_label(self):
        """NodeLabel を作成できる"""
        from labels.models import Label, NodeLabel
        from trees.models import JosekiTree, Node

        tree = JosekiTree.objects.create(name="テスト定跡")
        node = Node.objects.create(
            tree=tree,
            sfen="lnsgkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL b -",
        )
        label = Label.objects.create(name="急戦")

        node_label = NodeLabel.objects.create(node=node, label=label)

        assert node_label.id is not None
        assert isinstance(node_label.id, uuid.UUID)
        assert node_label.node == node
        assert node_label.label == label
        assert node_label.created_at is not None

    def test_node_label_unique_per_node(self):
        """同一ノードに同じラベルは付けられない"""
        from labels.models import Label, NodeLabel
        from trees.models import JosekiTree, Node

        tree = JosekiTree.objects.create(name="テスト定跡")
        node = Node.objects.create(
            tree=tree,
            sfen="lnsgkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL b -",
        )
        label = Label.objects.create(name="急戦")

        NodeLabel.objects.create(node=node, label=label)

        with pytest.raises(IntegrityError):
            NodeLabel.objects.create(node=node, label=label)

    def test_node_can_have_multiple_labels(self):
        """ノードには複数のラベルを付けられる"""
        from labels.models import Label, NodeLabel
        from trees.models import JosekiTree, Node

        tree = JosekiTree.objects.create(name="テスト定跡")
        node = Node.objects.create(
            tree=tree,
            sfen="lnsgkgsnl/1r5b1/ppppppppp/9/9/9/PPPPPPPPP/1B5R1/LNSGKGSNL b -",
        )
        label1 = Label.objects.create(name="急戦")
        label2 = Label.objects.create(name="矢倉")

        nl1 = NodeLabel.objects.create(node=node, label=label1)
        nl2 = NodeLabel.objects.create(node=node, label=label2)

        assert nl1.id != nl2.id
        assert node.node_labels.count() == 2

    def test_node_label_db_table(self):
        """NodeLabel のテーブル名"""
        from labels.models import NodeLabel

        assert NodeLabel._meta.db_table == "node_labels"

    def test_node_label_str(self):
        """NodeLabel の文字列表現"""
        from labels.models import Label, NodeLabel
        from trees.models import JosekiTree, Node

        tree = JosekiTree.objects.create(name="テスト")
        node = Node.objects.create(
            tree=tree,
            sfen="sfen b -",
        )
        label = Label.objects.create(name="急戦")
        node_label = NodeLabel.objects.create(node=node, label=label)

        assert "急戦" in str(node_label)
