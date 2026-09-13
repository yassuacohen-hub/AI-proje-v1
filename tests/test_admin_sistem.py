from __future__ import annotations

from unittest.mock import MagicMock

from web_dashboard.tabs import admin_sistem


def test_render_sistem_tab_composes_all_system_panels(monkeypatch):
    calls = []

    for name in [
        "render_webhook_monitor_tab",
        "render_dlq_tab",
        "render_performance_tab",
        "render_cost_tab",
        "render_api_analytics_tab",
    ]:
        monkeypatch.setattr(admin_sistem, name, lambda name=name: calls.append(name))

    for name in ["subheader", "caption", "divider", "info"]:
        monkeypatch.setattr(admin_sistem.st, name, MagicMock())
    monkeypatch.setattr(admin_sistem.st, "button", lambda *args, **kwargs: False)

    admin_sistem.render_sistem_tab()

    assert calls == [
        "render_webhook_monitor_tab",
        "render_dlq_tab",
        "render_performance_tab",
        "render_cost_tab",
        "render_api_analytics_tab",
    ]
    admin_sistem.st.subheader.assert_any_call("⚙️ Sistem")
    admin_sistem.st.info.assert_called_once()


def test_render_sistem_tab_shows_guidance_before_refresh_and_panels(monkeypatch):
    events = []
    monkeypatch.setattr(admin_sistem.st, "subheader", lambda *args, **kwargs: None)
    monkeypatch.setattr(admin_sistem.st, "caption", lambda *args, **kwargs: None)
    monkeypatch.setattr(admin_sistem.st, "info", lambda *args, **kwargs: events.append("info"))
    monkeypatch.setattr(admin_sistem.st, "button", lambda *args, **kwargs: events.append("refresh") or False)
    monkeypatch.setattr(admin_sistem.st, "divider", lambda: None)
    monkeypatch.setattr(admin_sistem, "render_webhook_monitor_tab", lambda: events.append("webhook"))
    monkeypatch.setattr(admin_sistem, "render_dlq_tab", lambda: events.append("dlq"))
    monkeypatch.setattr(admin_sistem, "render_performance_tab", lambda: events.append("performance"))
    monkeypatch.setattr(admin_sistem, "render_cost_tab", lambda: events.append("cost"))
    monkeypatch.setattr(admin_sistem, "render_api_analytics_tab", lambda: events.append("analytics"))

    admin_sistem.render_sistem_tab()

    assert events.index("info") < events.index("refresh")
    assert events.index("info") < events.index("webhook")
