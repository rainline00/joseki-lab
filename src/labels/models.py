"""
Labels app models.

ラベルとノード-ラベル関連のモデル定義
"""

import uuid

from django.core.validators import RegexValidator
from django.db import models


class Label(models.Model):
    """ラベル（戦型タグ）

    ノードに付与するタグ（急戦、持久戦など）
    """

    HEX_COLOR_VALIDATOR = RegexValidator(
        regex=r"^#[0-9A-Fa-f]{6}$",
        message="色は #RRGGBB 形式で指定してください",
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True, verbose_name="ラベル名")
    color = models.CharField(
        max_length=7,
        blank=True,
        validators=[HEX_COLOR_VALIDATOR],
        verbose_name="表示色（HEX）",
    )
    description = models.TextField(blank=True, verbose_name="説明")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")

    class Meta:
        db_table = "labels"
        ordering = ["name"]
        verbose_name = "ラベル"
        verbose_name_plural = "ラベル"

    def __str__(self) -> str:
        return self.name


class NodeLabel(models.Model):
    """ノード-ラベル関連

    ノードとラベルの多対多関連を管理
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    node = models.ForeignKey(
        "trees.Node",
        on_delete=models.CASCADE,
        related_name="node_labels",
        verbose_name="ノード",
    )
    label = models.ForeignKey(
        Label,
        on_delete=models.CASCADE,
        related_name="node_labels",
        verbose_name="ラベル",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="作成日時")

    class Meta:
        db_table = "node_labels"
        constraints = [
            models.UniqueConstraint(
                fields=["node", "label"], name="unique_label_per_node"
            )
        ]
        verbose_name = "ノード-ラベル関連"
        verbose_name_plural = "ノード-ラベル関連"

    def __str__(self) -> str:
        return f"{self.node} - {self.label}"
