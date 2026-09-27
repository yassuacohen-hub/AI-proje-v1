# -*- coding: utf-8 -*-
"""ADMIN-UX-PROFILMENU-01: Profil popover testleri."""
from __future__ import annotations

import pytest
from unittest.mock import MagicMock, patch

from src.company_master.ui.components.profil_menu import ProfileMenu, render_profil_menu


def test_profil_menu_olusturma() -> None:
    """ProfilMenu bileşeni başarıyla oluşturulur."""
    menu = ProfileMenu(kullanici_adi="Admin", rol="admin")
    assert menu.kullanici_adi == "Admin"
    assert menu.rol == "admin"
    assert menu.acik is False


def test_profil_menu_html_kapali() -> None:
    """Kapalıyken HTML boş döner."""
    menu = ProfileMenu(kullanici_adi="Test", acik=False)
    assert menu.html() == ""


def test_profil_menu_html_acik() -> None:
    """Açıkken HTML üretilir."""
    menu = ProfileMenu(kullanici_adi="TestUser", rol="editor", acik=True)
    html = menu.html()
    assert "TestUser" in html
    assert "editor" in html
    assert 'role="menu"' in html
    assert "Ayarlar" in html
    assert "Çıkış" in html


def test_profil_menu_avatar_monokrom() -> None:
    """Avatar monokrom sınıfı içerir."""
    menu = ProfileMenu(kullanici_adi="Admin", acik=True)
    html = menu.html()
    assert "avatar-monokrom" in html


def test_profil_menu_ayarlar_link() -> None:
    """Ayarlar linki doğru URL ile üretilir."""
    menu = ProfileMenu(kullanici_adi="Test", acik=True, ayarlar_url="?sayfa=ozel")
    html = menu.html()
    assert 'href="?sayfa=ozel"' in html


def test_profil_menu_cikis_link() -> None:
    """Çıkış linki doğru URL ile üretilir."""
    menu = ProfileMenu(kullanici_adi="Test", acik=True, cikis_url="?cikis=yap")
    html = menu.html()
    assert 'href="?cikis=yap"' in html


def test_render_profil_menu_yardimci() -> None:
    """render_profil_menu yardımcı fonksiyonu çalışır."""
    menu = render_profil_menu(kullanici_adi="Yardimci", rol="moderator", acik=True)
    assert isinstance(menu, ProfileMenu)
    assert menu.kullanici_adi == "Yardimci"
    assert menu.rol == "moderator"


def test_profil_menu_bos_kullanici_adi_hata() -> None:
    """Boş kullanıcı adı hata verir."""
    with pytest.raises(ValueError, match="Kullanıcı adı boş olamaz"):
        ProfileMenu(kullanici_adi="", acik=True)


def test_profil_menu_streamlit_cagrisi(monkeypatch) -> None:
    """streamlit() metodu çağrılır."""
    mock_st = MagicMock()
    monkeypatch.setattr("streamlit.markdown", mock_st.markdown)

    menu = ProfileMenu(kullanici_adi="Test", acik=True)
    menu.streamlit(container=mock_st)

    mock_st.markdown.assert_called_once()
    args, kwargs = mock_st.markdown.call_args
    assert "Test" in args[0]
    assert kwargs.get("unsafe_allow_html") is True


def test_profil_menu_import() -> None:
    """Modül import edilebilir."""
    from src.company_master.ui.components import profil_menu

    assert hasattr(profil_menu, "ProfileMenu")
    assert hasattr(profil_menu, "render_profil_menu")
