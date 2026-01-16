"""
Trees app configuration.

定跡ツリー管理アプリケーションの設定
"""

from django.apps import AppConfig


class TreesConfig(AppConfig):
    """Trees アプリケーション設定"""

    default_auto_field = "django.db.models.BigAutoField"
    name = "trees"
    verbose_name = "定跡ツリー管理"
