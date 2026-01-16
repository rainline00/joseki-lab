"""
Labels app configuration.

ラベル管理アプリケーションの設定
"""

from django.apps import AppConfig


class LabelsConfig(AppConfig):
    """Labels アプリケーション設定"""

    default_auto_field = "django.db.models.BigAutoField"
    name = "labels"
    verbose_name = "ラベル管理"
