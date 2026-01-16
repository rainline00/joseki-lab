"""
Exports app configuration.

エクスポート機能アプリケーションの設定
"""

from django.apps import AppConfig


class ExportsConfig(AppConfig):
    """Exports アプリケーション設定"""

    default_auto_field = "django.db.models.BigAutoField"
    name = "exports"
    verbose_name = "エクスポート機能"
