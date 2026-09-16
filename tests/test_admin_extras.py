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
    # Mock Streamlit renderini engellemek için st.subheader vb. işlemleri mock'la
    monkeypatch.setattr("web_dashboard.tabs.admin_extras.st.subheader", lambda x: None)
    monkeypatch.setattr("web_dashboard.tabs.admin_extras.st.dataframe", lambda *a, **kw: None)
    monkeypatch.setattr("web_dashboard.tabs.admin_extras.st.info", lambda x: None)
    monkeypatch.setattr("web_dashboard.tabs.admin_extras.st.json", lambda x: None)
    monkeypatch.setattr("web_dashboard.tabs.admin_extras.st.warning", lambda x: None)
    render_api_management()
    assert "/api/admin/api-usage" in calls


def test_render_user_management_with_mock(monkeypatch):
    from unittest.mock import MagicMock
    calls = []
    def fake_get(endpoint, **kwargs):
        calls.append(endpoint)
        if endpoint == "/api/admin/pending":
            return {"bekleyen": [{"user_id": "u2", "email": "u@x.com", "company_name": "X", "tier": "terminal"}], "onayli_son": []}
        if endpoint == "/api/admin/categories":
            return {"items": [{"code": "A", "label_tr": "Ana"}]}
        raise APIError("unexpected")
    monkeypatch.setattr("web_dashboard.tabs.admin_extras.get_api", fake_get)
    # Mock Streamlit renderini engellemek için tüm st fonksiyonlarını mock'la
    mock_ph = MagicMock()
    mock_ph.render = MagicMock()
    monkeypatch.setattr("web_dashboard.tabs.admin_extras.PageHeader", lambda *a, **kw: mock_ph)
    monkeypatch.setattr("web_dashboard.tabs.admin_extras.st.warning", MagicMock())
    mock_cols = [MagicMock() for _ in range(2)]
    monkeypatch.setattr("web_dashboard.tabs.admin_extras.st.columns", lambda n: mock_cols)
    monkeypatch.setattr("web_dashboard.tabs.admin_extras.st.selectbox", MagicMock(return_value="terminal"))
    monkeypatch.setattr("web_dashboard.tabs.admin_extras.st.write", MagicMock())
    monkeypatch.setattr("web_dashboard.tabs.admin_extras.st.button", MagicMock(return_value=False))
    mock_form = MagicMock()
    mock_form.__enter__ = MagicMock(return_value=mock_form)
    mock_form.__exit__ = MagicMock(return_value=False)
    monkeypatch.setattr("web_dashboard.tabs.admin_extras.st.form", MagicMock(return_value=mock_form))
    monkeypatch.setattr("web_dashboard.tabs.admin_extras.st.text_input", MagicMock(return_value=""))
    monkeypatch.setattr("web_dashboard.tabs.admin_extras.st.number_input", MagicMock(return_value=50))
    monkeypatch.setattr("web_dashboard.tabs.admin_extras.st.form_submit_button", MagicMock(return_value=False))
    monkeypatch.setattr("web_dashboard.tabs.admin_extras.st.dataframe", MagicMock())
    monkeypatch.setattr("web_dashboard.tabs.admin_extras.st.info", MagicMock())
    monkeypatch.setattr("web_dashboard.tabs.admin_extras.st.success", MagicMock())
    monkeypatch.setattr("web_dashboard.tabs.admin_extras.st.error", MagicMock())
    mock_cache = MagicMock()
    mock_cache.clear = MagicMock()
    monkeypatch.setattr("web_dashboard.tabs.admin_extras.st.cache_data", mock_cache)
    render_user_management(token="tok")
    assert "/api/admin/pending" in calls
    assert "/api/admin/categories" in calls