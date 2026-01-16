"""
WSGI config for Joseki Manager project.

将棋定跡管理アプリケーション - REST API バックエンド
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "joseki.settings")

application = get_wsgi_application()
