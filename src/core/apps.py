"""
Core app configuration.

共通機能アプリケーションの設定
"""

from django.apps import AppConfig


class CoreConfig(AppConfig):
    """Core アプリケーション設定"""

    default_auto_field = "django.db.models.BigAutoField"
    name = "core"
    verbose_name = "共通機能"
