"""
URL configuration for Trees app.

定跡ツリーとノードの REST API ルーティングを定義
"""

from django.urls import path

from trees.views import JosekiTreeViewSet, NodeViewSet

app_name = "trees"

# JosekiTreeViewSet のアクション
tree_list = JosekiTreeViewSet.as_view(
    {
        "get": "list",
        "post": "create",
    }
)

tree_detail = JosekiTreeViewSet.as_view(
    {
        "get": "retrieve",
        "patch": "partial_update",
    }
)

# NodeViewSet のアクション
node_add_move = NodeViewSet.as_view(
    {
        "post": "add_move",
    }
)

node_children = NodeViewSet.as_view(
    {
        "get": "children",
    }
)

node_delete = NodeViewSet.as_view(
    {
        "delete": "destroy",
    }
)

urlpatterns = [
    # Trees
    path("", tree_list, name="tree-list"),
    path("<str:pk>/", tree_detail, name="tree-detail"),
    # Nodes (nested under trees)
    path(
        "<str:tree_id>/nodes/<str:node_id>/moves/",
        node_add_move,
        name="node-add-move",
    ),
    path(
        "<str:tree_id>/nodes/<str:node_id>/children/",
        node_children,
        name="node-children",
    ),
    path(
        "<str:tree_id>/nodes/<str:node_id>/",
        node_delete,
        name="node-delete",
    ),
]
