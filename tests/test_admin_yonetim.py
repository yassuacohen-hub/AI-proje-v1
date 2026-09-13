from __future__ import annotations

from unittest.mock import MagicMock

from web_dashboard.tabs import admin_yonetim


def test_render_yonetim_tab_composes_management_panels(monkeypatch):
    calls = []

    monkeypatch.setattr(
        admin_yonetim,
        "render_api_management",
        lambda **kwargs: calls.append("api"),
    )
    monkeypatch.setattr(
        admin_yonetim,
        "render_user_management",
        lambda **kwargs: calls.append("users"),
    )
    monkeypatch.setattr(admin_yonetim, "render_search_tab", lambda: calls.append("search"))
    monkeypatch.setattr(admin_yonetim, "render_export_tab", lambda: calls.append("export"))
    monkeypatch.setattr(admin_yonetim, "render_auto_refresh", lambda: calls.append("refresh"))

    for name in ["subheader", "caption", "divider", "info"]:
        monkeypatch.setattr(admin_yonetim.st, name, MagicMock())
    monkeypatch.setattr(admin_yonetim.st, "button", lambda *args, **kwargs: False)
    monkeypatch.setattr(admin_yonetim.st, "session_state", {"admin_token": "test-token"})

    admin_yonetim.render_yonetim_tab()

    assert calls == ["api", "users", "search", "export", "refresh"]
    admin_yonetim.st.subheader.assert_any_call("🛠️ Yönetim")
    admin_yonetim.st.info.assert_called_once()
