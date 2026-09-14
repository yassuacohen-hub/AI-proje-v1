# -*- coding: utf-8 -*-
"""Sistem sekmesi davranış sözleşmesi (ADMIN-UI-10 sayfa iskeletiyle).

Ekran artık `st.subheader` kullanmaz; başlık `PageHeader` bileşeni üzerinden
`st.markdown(..., unsafe_allow_html=True)` ile yayınlanır. Testler bu yüzden
`st.markdown` çıktısını okur.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from web_dashboard.tabs import admin_sistem

PANELLER: tuple[str, ...] = (
    "render_webhook_monitor_tab",
    "render_dlq_tab",
    "render_performance_tab",
    "render_cost_tab",
    "render_api_analytics_tab",
)


def _markdown_metni(mock: MagicMock) -> str:
    """Tüm `st.markdown` çağrılarının ilk konumsal argümanını birleştirir."""
    return "\n".join(str(cagri.args[0]) for cagri in mock.call_args_list if cagri.args)


def _columns_sahte(spec, **_kwargs):
    """`vertical_alignment` gibi kwarg'ları sessizce yutan kolon sahtesi."""
    adet = spec if isinstance(spec, int) else len(spec)
    return [MagicMock() for _ in range(adet)]


@pytest.fixture
def st_sahte(monkeypatch) -> dict[str, MagicMock]:
    """Ekranı yan etkisiz çalıştıran ortak Streamlit sahtesi."""
    kaydedilen = {ad: MagicMock() for ad in ("markdown", "caption", "divider", "info")}
    for ad, mock in kaydedilen.items():
        monkeypatch.setattr(admin_sistem.st, ad, mock)

    monkeypatch.setattr(admin_sistem.st, "button", lambda *a, **k: False)
    monkeypatch.setattr(admin_sistem.st, "columns", _columns_sahte)
    return kaydedilen


def test_render_sistem_tab_composes_all_system_panels(monkeypatch, st_sahte):
    """Tüm sistem panelleri tanımlı sırayla çizilmeli."""
    calls: list[str] = []
    for name in PANELLER:
        monkeypatch.setattr(admin_sistem, name, lambda name=name: calls.append(name))

    admin_sistem.render_sistem_tab()

    assert calls == list(PANELLER)


def test_render_sistem_tab_sayfa_iskeleti_h1_uretir(monkeypatch, st_sahte):
    """ADMIN-UI-10 sözleşmesi: ekran tek bir H1 ve giriş paragrafı yayınlar."""
    for name in PANELLER:
        monkeypatch.setattr(admin_sistem, name, lambda: None)

    admin_sistem.render_sistem_tab()

    metin = _markdown_metni(st_sahte["markdown"])
    assert metin.count("<h1") == 1, "Ekranda tam olarak bir H1 olmalı."
    assert "Sistem" in metin
    assert admin_sistem.GIRIS_METNI in metin


def test_render_sistem_tab_shows_guidance_before_refresh_and_panels(monkeypatch):
    """Rehber metni yenile butonundan ve panellerden önce yayınlanmalı."""
    events: list[str] = []

    monkeypatch.setattr(
        admin_sistem.st,
        "markdown",
        lambda govde="", **k: events.append(
            "giris" if admin_sistem.GIRIS_METNI in str(govde) else "markdown"
        ),
    )
    monkeypatch.setattr(admin_sistem.st, "caption", lambda *a, **k: None)
    monkeypatch.setattr(admin_sistem.st, "divider", lambda *a, **k: None)
    monkeypatch.setattr(admin_sistem.st, "info", lambda *a, **k: None)
    monkeypatch.setattr(admin_sistem.st, "columns", _columns_sahte)
    monkeypatch.setattr(
        admin_sistem.st,
        "button",
        lambda *a, **k: events.append("refresh") or False,
    )
    for name in PANELLER:
        monkeypatch.setattr(admin_sistem, name, lambda name=name: events.append(name))

    admin_sistem.render_sistem_tab()

    assert "giris" in events, "Giriş metni PageHeader üzerinden yayınlanmalı."
    assert events.index("giris") < events.index("refresh")
    assert events.index("giris") < events.index(PANELLER[0])


def test_render_sistem_tab_bolum_gezinmesi_yayinlanir(monkeypatch, st_sahte):
    """SectionNav bağlantıları bölüm kimlikleriyle eşleşmeli."""
    for name in PANELLER:
        monkeypatch.setattr(admin_sistem, name, lambda: None)

    admin_sistem.render_sistem_tab()

    metin = _markdown_metni(st_sahte["markdown"])
    for bolum in admin_sistem.BOLUMLER:
        assert f'id="{bolum.kimlik}"' in metin or f'href="#{bolum.kimlik}"' in metin
