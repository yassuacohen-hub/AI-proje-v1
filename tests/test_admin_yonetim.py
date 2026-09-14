# -*- coding: utf-8 -*-
"""Yönetim sekmesi davranış sözleşmesi (ADMIN-UI-10 sayfa iskeletiyle).

Ekran artık `st.subheader` kullanmaz; başlık `PageHeader` bileşeni üzerinden
`st.markdown(..., unsafe_allow_html=True)` ile yayınlanır.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from web_dashboard.tabs import admin_yonetim

SIRA: list[str] = ["api", "users", "search", "export", "refresh"]


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
        monkeypatch.setattr(admin_yonetim.st, ad, mock)

    monkeypatch.setattr(admin_yonetim.st, "button", lambda *a, **k: False)
    monkeypatch.setattr(admin_yonetim.st, "columns", _columns_sahte)
    monkeypatch.setattr(admin_yonetim.st, "session_state", {"admin_token": "test-token"})
    return kaydedilen


@pytest.fixture
def panel_cagrilari(monkeypatch) -> list[str]:
    """Yönetim panellerini sahteleyip çağrı sırasını kaydeder."""
    calls: list[str] = []
    monkeypatch.setattr(
        admin_yonetim, "render_api_management", lambda **k: calls.append("api")
    )
    monkeypatch.setattr(
        admin_yonetim, "render_user_management", lambda **k: calls.append("users")
    )
    monkeypatch.setattr(admin_yonetim, "render_search_tab", lambda: calls.append("search"))
    monkeypatch.setattr(admin_yonetim, "render_export_tab", lambda: calls.append("export"))
    monkeypatch.setattr(admin_yonetim, "render_auto_refresh", lambda: calls.append("refresh"))
    return calls


def test_render_yonetim_tab_composes_management_panels(st_sahte, panel_cagrilari):
    """Tüm yönetim panelleri tanımlı sırayla çizilmeli."""
    admin_yonetim.render_yonetim_tab()

    assert panel_cagrilari == SIRA


def test_render_yonetim_tab_sayfa_iskeleti_h1_uretir(st_sahte, panel_cagrilari):
    """ADMIN-UI-10 sözleşmesi: ekran tek bir H1 ve giriş paragrafı yayınlar."""
    admin_yonetim.render_yonetim_tab()

    metin = _markdown_metni(st_sahte["markdown"])
    assert metin.count("<h1") == 1, "Ekranda tam olarak bir H1 olmalı."
    assert "Yönetim" in metin
    assert admin_yonetim.GIRIS_METNI in metin


def test_render_yonetim_tab_bolum_gezinmesi_yayinlanir(st_sahte, panel_cagrilari):
    """SectionNav bağlantıları bölüm kimlikleriyle eşleşmeli."""
    admin_yonetim.render_yonetim_tab()

    metin = _markdown_metni(st_sahte["markdown"])
    for bolum in admin_yonetim.BOLUMLER:
        assert f'id="{bolum.kimlik}"' in metin or f'href="#{bolum.kimlik}"' in metin
