# -*- coding: utf-8 -*-
"""Müşteriler sekmesi davranış testleri.

ADMIN-UI-10 sonrası ekran iskeleti ``PageHeader -> SectionNav -> Section``
kalıbına taşındı. Başlık artık ``st.subheader`` ile değil, ``st.markdown``
üzerinden akan semantik HTML (``<h1>``) ile üretiliyor; bu yüzden sözleşme
kanıtı olarak ``st.markdown`` çağrıları okunur.

Ayrıca aksiyon şeridi ``st.columns(..., vertical_alignment="center")``
kullandığı için Streamlit sahtesi anahtar kelime argümanlarını yutmalıdır.
"""
from __future__ import annotations

from unittest.mock import MagicMock

import pandas as pd
import pytest

from web_dashboard.tabs import admin_musteriler


def _markdown_metni(mock: MagicMock) -> str:
    """Tüm `st.markdown` çağrılarının ilk konumsal argümanını birleştirir."""
    return "\n".join(str(cagri.args[0]) for cagri in mock.call_args_list if cagri.args)


@pytest.fixture
def st_sahte(monkeypatch) -> dict[str, MagicMock]:
    """Ekranı yan etkisiz çalıştıran ortak Streamlit sahtesi."""
    kaydedilen = {
        ad: MagicMock()
        for ad in ("markdown", "caption", "info", "success", "dataframe")
    }
    for ad, mock in kaydedilen.items():
        monkeypatch.setattr(admin_musteriler.st, ad, mock)

    monkeypatch.setattr(admin_musteriler.st, "button", lambda *a, **k: False)
    monkeypatch.setattr(admin_musteriler.st, "toggle", lambda *a, **k: False)
    monkeypatch.setattr(admin_musteriler.st, "slider", lambda *a, **k: (0, 100))
    # NOT: `vertical_alignment` gibi kwarg'ları sessizce yutmalı (ADMIN-UI-10).
    monkeypatch.setattr(
        admin_musteriler.st,
        "columns",
        lambda spec, **k: [
            MagicMock() for _ in range(spec if isinstance(spec, int) else len(spec))
        ],
    )
    return kaydedilen


def test_render_musteriler_shows_empty_state(monkeypatch, st_sahte):
    monkeypatch.setattr(admin_musteriler, "load_admin_kpi_summary", lambda: {})
    monkeypatch.setattr(admin_musteriler, "get_source_names", lambda: [])
    monkeypatch.setattr(admin_musteriler, "search_companies", lambda **kwargs: None)
    monkeypatch.setattr(admin_musteriler.st, "text_input", lambda *a, **k: "")
    monkeypatch.setattr(
        admin_musteriler.st,
        "selectbox",
        lambda *a, **k: "Tümü" if "Kaynak" in a[0] else 50,
    )

    admin_musteriler.render_musteriler_tab()

    assert any(
        "Veri gelince firma listesi" in str(cagri)
        for cagri in st_sahte["info"].call_args_list
    )


def test_render_musteriler_renders_filtered_companies(monkeypatch, st_sahte):
    frame = pd.DataFrame([{"legal_name": "Test Firma", "data_quality_score": 82.0}])
    monkeypatch.setattr(
        admin_musteriler,
        "load_admin_kpi_summary",
        lambda: {"sinyal_toplam": 3, "son_24s_yeni_firma": 1},
    )
    monkeypatch.setattr(admin_musteriler, "get_source_names", lambda: [])
    monkeypatch.setattr(admin_musteriler, "search_companies", lambda **kwargs: frame)
    monkeypatch.setattr(admin_musteriler.st, "text_input", lambda *a, **k: "Test")
    monkeypatch.setattr(
        admin_musteriler.st,
        "selectbox",
        lambda *a, **k: "Tümü" if "Kaynak" in a[0] else 50,
    )

    admin_musteriler.render_musteriler_tab()

    st_sahte["dataframe"].assert_called_once_with(
        frame, use_container_width=True, hide_index=True
    )


def test_render_musteriler_sayfa_iskeleti_h1_uretir(monkeypatch, st_sahte):
    """ADMIN-UI-10 sözleşmesi: ekran tek bir H1 ve giriş paragrafı yayınlar."""
    monkeypatch.setattr(admin_musteriler, "load_admin_kpi_summary", lambda: {})
    monkeypatch.setattr(admin_musteriler, "get_source_names", lambda: [])
    monkeypatch.setattr(admin_musteriler, "search_companies", lambda **kwargs: None)
    monkeypatch.setattr(admin_musteriler.st, "text_input", lambda *a, **k: "")
    monkeypatch.setattr(
        admin_musteriler.st,
        "selectbox",
        lambda *a, **k: "Tümü" if "Kaynak" in a[0] else 50,
    )

    admin_musteriler.render_musteriler_tab()

    metin = _markdown_metni(st_sahte["markdown"])
    assert metin.count("<h1") == 1, "Ekranda tam olarak bir H1 olmalı."
    assert "Müşteriler" in metin
    assert admin_musteriler.GIRIS_METNI in metin
