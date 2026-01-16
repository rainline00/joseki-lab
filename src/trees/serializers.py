"""
Serializers for Trees app.

定跡ツリー、ノード、エッジの入出力シリアライザを定義
"""

from rest_framework import serializers

from trees.models import Edge, JosekiTree, Node


# ============================================================================
# JosekiTree Serializers
# ============================================================================


class JosekiTreeCreateSerializer(serializers.Serializer):
    """POST /trees 入力用シリアライザ"""

    name = serializers.CharField(max_length=200, min_length=1)
    description = serializers.CharField(
        required=False, allow_blank=True, default=""
    )


class JosekiTreeUpdateSerializer(serializers.Serializer):
    """PATCH /trees/{id} 入力用シリアライザ"""

    name = serializers.CharField(max_length=200, min_length=1, required=False)
    description = serializers.CharField(required=False, allow_blank=True)


# ============================================================================
# Node Serializers
# ============================================================================


class NodeSerializer(serializers.ModelSerializer):
    """ノード出力（基本）"""

    is_root = serializers.BooleanField(read_only=True)

    class Meta:
        model = Node
        fields = [
            "id",
            "tree_id",
            "sfen",
            "ply",
            "comment",
            "evaluation",
            "metadata",
            "is_root",
            "created_at",
            "updated_at",
        ]


class ParentEdgeSerializer(serializers.Serializer):
    """親エッジ情報"""

    parent_id = serializers.UUIDField(source="parent.id")
    parent_sfen = serializers.CharField(source="parent.sfen")
    move_usi = serializers.CharField()
    move_japanese = serializers.CharField()


class ChildNodeSerializer(serializers.Serializer):
    """子ノード情報（エッジ付き）"""

    node = NodeSerializer()
    move_usi = serializers.CharField()
    move_japanese = serializers.CharField()


class NodeDetailSerializer(serializers.ModelSerializer):
    """ノード詳細出力（親子情報付き）"""

    is_root = serializers.BooleanField(read_only=True)
    parents = serializers.SerializerMethodField()
    children = serializers.SerializerMethodField()

    class Meta:
        model = Node
        fields = [
            "id",
            "tree_id",
            "sfen",
            "ply",
            "comment",
            "evaluation",
            "metadata",
            "is_root",
            "created_at",
            "updated_at",
            "parents",
            "children",
        ]

    def get_parents(self, obj):
        edges = obj.parent_edges.select_related("parent").all()
        return ParentEdgeSerializer(edges, many=True).data

    def get_children(self, obj):
        edges = obj.child_edges.select_related("child").all()
        return [
            {
                "node": NodeSerializer(edge.child).data,
                "move_usi": edge.move_usi,
                "move_japanese": edge.move_japanese,
            }
            for edge in edges
        ]


# ============================================================================
# JosekiTree Output Serializers
# ============================================================================


class JosekiTreeSummarySerializer(serializers.ModelSerializer):
    """GET /trees 一覧出力"""

    node_count = serializers.SerializerMethodField()

    class Meta:
        model = JosekiTree
        fields = [
            "id",
            "name",
            "description",
            "node_count",
            "created_at",
            "updated_at",
            "is_deleted",
            "deleted_at",
        ]

    def get_node_count(self, obj):
        return obj.nodes.count()


class JosekiTreeSerializer(serializers.ModelSerializer):
    """GET /trees/{id} 出力（root_node 付き）"""

    root_node = serializers.SerializerMethodField()
    node_count = serializers.SerializerMethodField()

    class Meta:
        model = JosekiTree
        fields = [
            "id",
            "name",
            "description",
            "node_count",
            "created_at",
            "updated_at",
            "is_deleted",
            "deleted_at",
            "root_node",
        ]

    def get_root_node(self, obj):
        root = obj.root_node
        if root:
            return NodeSerializer(root).data
        return None

    def get_node_count(self, obj):
        return obj.nodes.count()


# ============================================================================
# Edge Serializers
# ============================================================================


class EdgeSerializer(serializers.ModelSerializer):
    """エッジ出力"""

    class Meta:
        model = Edge
        fields = ["id", "move_usi", "move_japanese"]


# ============================================================================
# Move Serializers
# ============================================================================


class MoveCreateSerializer(serializers.Serializer):
    """POST /nodes/{id}/moves 入力用シリアライザ"""

    move_usi = serializers.CharField(max_length=10, min_length=1)

    def validate_move_usi(self, value):
        """USI 形式の基本チェック（詳細は Service 層で検証）"""
        if not value or not value.strip():
            raise serializers.ValidationError(
                "指し手は必須です"
            )
        return value.strip()


class MoveResultSerializer(serializers.Serializer):
    """POST /nodes/{id}/moves 出力"""

    edge = EdgeSerializer()
    child_node = NodeSerializer()
    is_transposition = serializers.BooleanField()


class MoveErrorSerializer(serializers.Serializer):
    """エラー出力"""

    error = serializers.ChoiceField(
        choices=[
            "illegal_move",
            "nifu",
            "uchifuzume",
            "invalid_format",
            "duplicate_move",
            "cannot_delete_root",
            "parent_id_required",
        ]
    )
    message = serializers.CharField()
    move_usi = serializers.CharField(required=False)
