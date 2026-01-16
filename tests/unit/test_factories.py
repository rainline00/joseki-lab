"""
Factory tests for Joseki Manager.

ファクトリを使用したオブジェクト生成のテスト
"""

import pytest


@pytest.mark.django_db
class TestJosekiTreeFactory:
    """JosekiTreeFactory のテスト"""

    def test_create_joseki_tree(self):
        """JosekiTree を作成できる"""
        from tests.factories import JosekiTreeFactory

        tree = JosekiTreeFactory()

        assert tree.id is not None
        assert tree.name is not None
        assert "定跡ツリー" in tree.name

    def test_create_joseki_tree_with_custom_name(self):
        """カスタム名で JosekiTree を作成できる"""
        from tests.factories import JosekiTreeFactory

        tree = JosekiTreeFactory(name="矢倉定跡")

        assert tree.name == "矢倉定跡"

    def test_create_multiple_trees(self):
        """複数の JosekiTree を作成できる"""
        from tests.factories import JosekiTreeFactory

        tree1 = JosekiTreeFactory()
        tree2 = JosekiTreeFactory()

        assert tree1.id != tree2.id
        assert tree1.name != tree2.name


@pytest.mark.django_db
class TestNodeFactory:
    """NodeFactory のテスト"""

    def test_create_node(self):
        """Node を作成できる"""
        from tests.factories import NodeFactory

        node = NodeFactory()

        assert node.id is not None
        assert node.tree is not None
        assert node.sfen is not None
        assert node.ply == 0

    def test_create_node_with_tree(self):
        """指定したツリーに Node を作成できる"""
        from tests.factories import JosekiTreeFactory, NodeFactory

        tree = JosekiTreeFactory(name="テスト定跡")
        node = NodeFactory(tree=tree)

        assert node.tree == tree
        assert node.tree.name == "テスト定跡"

    def test_create_root_node(self):
        """RootNodeFactory でルートノードを作成できる"""
        from tests.factories import INITIAL_SFEN, RootNodeFactory

        node = RootNodeFactory()

        assert node.sfen == INITIAL_SFEN
        assert node.ply == 0

    def test_create_multiple_nodes(self):
        """複数の Node を作成できる"""
        from tests.factories import JosekiTreeFactory, NodeFactory

        tree = JosekiTreeFactory()
        node1 = NodeFactory(tree=tree)
        node2 = NodeFactory(tree=tree)

        assert node1.id != node2.id
        # 同一ツリー内ではユニークな SFEN が必要
        assert node1.sfen != node2.sfen


@pytest.mark.django_db
class TestEdgeFactory:
    """EdgeFactory のテスト"""

    def test_create_edge(self):
        """Edge を作成できる"""
        from tests.factories import EdgeFactory

        edge = EdgeFactory()

        assert edge.id is not None
        assert edge.parent is not None
        assert edge.child is not None
        assert edge.move_usi is not None

    def test_edge_parent_child_same_tree(self):
        """Edge の parent と child は同じツリーに属する"""
        from tests.factories import EdgeFactory

        edge = EdgeFactory()

        assert edge.parent.tree == edge.child.tree

    def test_edge_child_ply_incremented(self):
        """Edge の child の ply は parent + 1"""
        from tests.factories import EdgeFactory

        edge = EdgeFactory()

        assert edge.child.ply == edge.parent.ply + 1

    def test_create_edge_with_custom_move(self):
        """カスタム指し手で Edge を作成できる"""
        from tests.factories import EdgeFactory, NodeFactory

        parent = NodeFactory()
        child = NodeFactory(tree=parent.tree, ply=1)
        edge = EdgeFactory(parent=parent, child=child, move_usi="2g2f")

        assert edge.move_usi == "2g2f"


@pytest.mark.django_db
class TestLabelFactory:
    """LabelFactory のテスト"""

    def test_create_label(self):
        """Label を作成できる"""
        from tests.factories import LabelFactory

        label = LabelFactory()

        assert label.id is not None
        assert label.name is not None
        assert label.color == "#FF0000"

    def test_create_label_with_custom_color(self):
        """カスタム色で Label を作成できる"""
        from tests.factories import LabelFactory

        label = LabelFactory(color="#00FF00")

        assert label.color == "#00FF00"

    def test_create_multiple_labels(self):
        """複数の Label を作成できる"""
        from tests.factories import LabelFactory

        label1 = LabelFactory()
        label2 = LabelFactory()

        assert label1.id != label2.id
        assert label1.name != label2.name


@pytest.mark.django_db
class TestNodeLabelFactory:
    """NodeLabelFactory のテスト"""

    def test_create_node_label(self):
        """NodeLabel を作成できる"""
        from tests.factories import NodeLabelFactory

        node_label = NodeLabelFactory()

        assert node_label.id is not None
        assert node_label.node is not None
        assert node_label.label is not None

    def test_create_node_label_with_existing_objects(self):
        """既存の Node と Label で NodeLabel を作成できる"""
        from tests.factories import LabelFactory, NodeFactory, NodeLabelFactory

        node = NodeFactory()
        label = LabelFactory(name="急戦")
        node_label = NodeLabelFactory(node=node, label=label)

        assert node_label.node == node
        assert node_label.label == label
        assert node_label.label.name == "急戦"


@pytest.mark.django_db
class TestFactoryIntegration:
    """ファクトリ統合テスト"""

    def test_create_tree_with_nodes_and_edges(self):
        """ツリー、ノード、エッジを一括で作成できる"""
        from tests.factories import (
            EdgeFactory,
            JosekiTreeFactory,
            NodeFactory,
            RootNodeFactory,
        )

        tree = JosekiTreeFactory(name="矢倉定跡")
        root = RootNodeFactory(tree=tree)
        child1 = NodeFactory(tree=tree, ply=1)
        child2 = NodeFactory(tree=tree, ply=1)

        edge1 = EdgeFactory(parent=root, child=child1, move_usi="7g7f")
        edge2 = EdgeFactory(parent=root, child=child2, move_usi="2g2f")

        assert tree.nodes.count() == 3
        assert root.child_edges.count() == 2
        assert edge1.parent == root
        assert edge2.parent == root

    def test_create_tree_with_labels(self):
        """ツリーとラベルを関連付けできる"""
        from tests.factories import (
            JosekiTreeFactory,
            LabelFactory,
            NodeLabelFactory,
            RootNodeFactory,
        )

        tree = JosekiTreeFactory(name="急戦矢倉")
        node = RootNodeFactory(tree=tree)
        label1 = LabelFactory(name="急戦")
        label2 = LabelFactory(name="矢倉")

        NodeLabelFactory(node=node, label=label1)
        NodeLabelFactory(node=node, label=label2)

        assert node.node_labels.count() == 2
