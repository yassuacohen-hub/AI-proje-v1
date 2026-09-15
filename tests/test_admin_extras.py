# -*- coding: utf-8 -*-
from unittest.mock import patch
from scripts.dash04_api_client import APIError
from web_dashboard.tabs.admin_extras import render_api_management, render_user_management


def test_render_functions_exist():
    assert callable(render_api_management)
    assert callable(render_user_management)


def test_render_api_management_with_mock(monkeypatch):
    calls = []
    def fake_get(endpoint, **kwargs):
        calls.append(endpoint)
        if endpoint == "/api/admin/api-usage":
            return {"items": [{"user_id": "u1", "requests": 5}], "rate_limits": {"requests": 100}}
        raise APIError("unexpected")
    monkeypatch.setattr("web_dashboard.tabs.admin_extras.get_api", fake_get)
    render_api_management()
    assert "/api/admin/api-usage" in calls


def test_render_user_management_with_mock(monkeypatch):
    calls = []
    def fake_get(endpoint, **kwargs):
        calls.append(endpoint)
        if endpoint == "/api/admin/pending":
            return {"bekleyen": [{"user_id": "u2"}], "onayli_son": []}
        if endpoint == "/api/admin/categories":
            return {"items": [{"code": "A", "label_tr": "Ana"}]}
        raise APIError("unexpected")
    monkeypatch.setattr("web_dashboard.tabs.admin_extras.get_api", fake_get)
    render_user_management()
    assert "/api/admin/pending" in calls
    assert "/api/admin/categories" in calls