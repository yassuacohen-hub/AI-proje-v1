from __future__ import annotations

from unittest.mock import MagicMock

import pandas as pd

from web_dashboard.tabs import admin_musteriler


def test_render_musteriler_shows_empty_state(monkeypatch):
    monkeypatch.setattr(admin_musteriler, "load_admin_kpi_summary", lambda: {})
    monkeypatch.setattr(admin_musteriler, "get_source_names", lambda: [])
    monkeypatch.setattr(admin_musteriler, "search_companies", lambda **kwargs: None)
    monkeypatch.setattr(admin_musteriler.st, "subheader", MagicMock())
    monkeypatch.setattr(admin_musteriler.st, "caption", MagicMock())
    info = MagicMock()
    monkeypatch.setattr(admin_musteriler.st, "info", info)
    monkeypatch.setattr(admin_musteriler.st, "text_input", lambda *args, **kwargs: "")
    monkeypatch.setattr(admin_musteriler.st, "slider", lambda *args, **kwargs: (0, 100))
    monkeypatch.setattr(admin_musteriler.st, "selectbox", lambda *args, **kwargs: "Tümü" if "Kaynak" in args[0] else 50)
    monkeypatch.setattr(admin_musteriler.st, "columns", lambda n: [MagicMock() for _ in range(n if isinstance(n, int) else len(n))])

    admin_musteriler.render_musteriler_tab()

    assert any("Veri gelince firma listesi" in str(call) for call in info.call_args_list)


def test_render_musteriler_renders_filtered_companies(monkeypatch):
    frame = pd.DataFrame([{"legal_name": "Test Firma", "data_quality_score": 82.0}])
    monkeypatch.setattr(admin_musteriler, "load_admin_kpi_summary", lambda: {"sinyal_toplam": 3, "son_24s_yeni_firma": 1})
    monkeypatch.setattr(admin_musteriler, "get_source_names", lambda: [])
    monkeypatch.setattr(admin_musteriler, "search_companies", lambda **kwargs: frame)
    monkeypatch.setattr(admin_musteriler.st, "subheader", MagicMock())
    monkeypatch.setattr(admin_musteriler.st, "caption", MagicMock())
    monkeypatch.setattr(admin_musteriler.st, "info", MagicMock())
    monkeypatch.setattr(admin_musteriler.st, "success", MagicMock())
    monkeypatch.setattr(admin_musteriler.st, "dataframe", MagicMock())
    monkeypatch.setattr(admin_musteriler.st, "text_input", lambda *args, **kwargs: "Test")
    monkeypatch.setattr(admin_musteriler.st, "slider", lambda *args, **kwargs: (0, 100))
    monkeypatch.setattr(admin_musteriler.st, "selectbox", lambda *args, **kwargs: "Tümü" if "Kaynak" in args[0] else 50)
    monkeypatch.setattr(admin_musteriler.st, "columns", lambda n: [MagicMock() for _ in range(n if isinstance(n, int) else len(n))])

    admin_musteriler.render_musteriler_tab()

    admin_musteriler.st.dataframe.assert_called_once_with(frame, use_container_width=True, hide_index=True)
