"""
pytest configuration for Joseki Manager tests.

pytest-django の設定と共通フィクスチャを定義
"""

import pytest


@pytest.fixture
def api_client():
    """DRF APIClient インスタンスを提供するフィクスチャ"""
    from rest_framework.test import APIClient

    return APIClient()


@pytest.fixture
def db_session(db):
    """
    データベースセッションを提供するフィクスチャ

    db フィクスチャに依存し、テスト用データベースへのアクセスを提供
    """
    return db
