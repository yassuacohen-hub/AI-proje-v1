# -*- coding: utf-8 -*-
"""KPI-EXA-02 (d): giriş sonrası sol menü büyümeli.

Sahip bulgusu: "giriş yapınca menüler çoğalmıyor". Bu test iki katmanda
doğrular:
1. Saf rol filtresi (`gorunur_bolumler`) — admin > analyst > anon.
2. `app.py` AppTest: `admin_token` oturumda varken sidebar'da daha fazla
   `nav_*` düğmesi olmalı ve yeni "Teknik Altyapı" bölümü görünmeli.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from web_dashboard.tabs import gorunur_bolumler, tab_getir  # noqa: E402


def test_rol_filtresi_kademeli_buyur():
    anon = {t.anahtar for t in gorunur_bolumler("anon")}
    analyst = {t.anahtar for t in gorunur_bolumler("analyst")}
    admin = {t.anahtar for t in gorunur_bolumler("admin")}
    assert anon < analyst <= admin
    assert "teknik_altyapi" in analyst and "teknik_altyapi" not in anon


def test_teknik_altyapi_tanimi():
    tanim = tab_getir("teknik_altyapi")
    assert tanim is not None
    assert tanim.url_path == "teknik-altyapi"
    assert tanim.min_rol == "analyst"


def _nav_anahtarlari(at) -> set[str]:
    return {str(b.key) for b in at.sidebar.button if str(b.key).startswith("nav_")}


def test_admin_token_menuyu_buyutur():
    from streamlit.testing.v1 import AppTest

    anon = AppTest.from_file(str(ROOT / "app.py"), default_timeout=90)
    anon.run()
    assert not anon.exception, [e.value for e in anon.exception]
    anon_nav = _nav_anahtarlari(anon)

    admin = AppTest.from_file(str(ROOT / "app.py"), default_timeout=90)
    admin.session_state["admin_token"] = "test-token"
    admin.run()
    assert not admin.exception, [e.value for e in admin.exception]
    admin_nav = _nav_anahtarlari(admin)

    assert anon_nav, "anon menüsü boş olmamalı"
    assert admin_nav > anon_nav, f"menü büyümedi: anon={len(anon_nav)} admin={len(admin_nav)}"
    assert "nav_teknik_altyapi" in admin_nav
