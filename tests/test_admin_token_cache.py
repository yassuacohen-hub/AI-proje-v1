# -*- coding: utf-8 -*-
"""K1-7: Admin token disk kalıcılığı — yaz/sil çevrimi.

`app.py::main()` AppSession reset sonrası `~/.streamlit_token_cache/admin_token.txt`
dosyasından token okuyor; yazıcı taraf yoktu → giriş her yenilemede düşüyordu.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from web_dashboard.tabs import admin_auth  # noqa: E402


def test_token_cache_yaz_ve_sil(tmp_path, monkeypatch) -> None:
    hedef = tmp_path / "cache" / "admin_token.txt"
    monkeypatch.setattr(admin_auth, "_TOKEN_CACHE", hedef)

    admin_auth.token_cache_yaz("tok-123")
    assert hedef.read_text(encoding="utf-8") == "tok-123"

    admin_auth.token_cache_sil()
    assert not hedef.exists()

    # İkinci silme hata vermemeli (missing_ok).
    admin_auth.token_cache_sil()


def test_yazilamaz_yol_sessiz_gecer(tmp_path, monkeypatch) -> None:
    """Kalıcılık kaybı giriş akışını bozmamalı — istisna yukarı sızmaz."""
    dosya = tmp_path / "dosya"
    dosya.write_text("x", encoding="utf-8")
    monkeypatch.setattr(admin_auth, "_TOKEN_CACHE", dosya / "alt" / "token.txt")
    admin_auth.token_cache_yaz("tok")  # NotADirectoryError yutulur


def test_login_ve_cikis_cache_cagiriyor() -> None:
    """Giriş token yazar, çıkış siler."""
    kod = (ROOT / "web_dashboard" / "tabs" / "admin_auth.py").read_text(encoding="utf-8")
    assert "token_cache_yaz(result[\"token\"])" in kod
    govde = kod.split("def admin_cikis()")[1].split("\ndef ")[0]
    assert "token_cache_sil()" in govde


def test_popover_sifre_degistir_etiketi() -> None:
    """K1-6: test_nav_ia04 tam metin 'Şifre Değiştir' arıyor."""
    kod = (ROOT / "app.py").read_text(encoding="utf-8")
    govde = kod.split("def _hesap_karti_popover()")[1].split("\ndef ")[0]
    assert "Şifre Değiştir" in govde
