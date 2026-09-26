# -*- coding: utf-8 -*-
"""AUTH-LOCKOUT-FIX-01: hesap kilidi yardimcilari.

Kapsanan kusurlar:
1. `INTERVAL ':lockout_minutes minutes'` — bind parametresi SQL metin sabitinin
   icinde kaldigi icin hic yerine konmuyordu; kilit suresi hic yazilmiyordu.
2. `except Exception: return False` — DB hatasinda fail-open; guvenlik kontrolu
   sessizce atlaniyordu.
3. Sureli kilidi temizleyen UPDATE `connect()` blogundaydi; commit olmuyordu.
4. `_log_search_event` dosyada iki kez tanimliydi (ikiz yapi).
"""
from __future__ import annotations

import ast
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest
from sqlalchemy import create_engine, text

WEB_APP = Path(__file__).resolve().parents[1] / "web_app.py"
KAYNAK = WEB_APP.read_text(encoding="utf-8", errors="replace")


def _motor():
    """Bellekte SQLite users tablosu (NOW() yok -> bind edilen ts sart)."""
    eng = create_engine("sqlite://")
    with eng.begin() as c:
        c.execute(text(
            "CREATE TABLE users (user_id TEXT PRIMARY KEY, "
            "failed_login_attempts INTEGER DEFAULT 0, locked_until TIMESTAMP)"
        ))
        c.execute(text("INSERT INTO users (user_id, failed_login_attempts) VALUES ('u1', 0)"))
    return eng


# --- 1. kilit suresi gercekten yaziliyor mu ------------------------------------
def test_kilit_suresi_bind_ediliyor():
    import web_app

    eng = _motor()
    for _ in range(web_app._LOGIN_MAX_ATTEMPTS):
        web_app._record_failed_login(eng, "u1")
    with eng.connect() as c:
        row = c.execute(text("SELECT failed_login_attempts, locked_until FROM users")).mappings().first()
    assert row["failed_login_attempts"] == web_app._LOGIN_MAX_ATTEMPTS
    assert row["locked_until"] is not None, "esik asildi ama locked_until yazilmadi"
    assert web_app._is_account_locked(eng, "u1") is True


def test_esik_altinda_kilit_yok():
    import web_app

    eng = _motor()
    web_app._record_failed_login(eng, "u1")
    with eng.connect() as c:
        assert c.execute(text("SELECT locked_until FROM users")).scalar() is None
    assert web_app._is_account_locked(eng, "u1") is False


# --- 2. suresi dolan kilit temizleniyor + commit oluyor ------------------------
def test_suresi_dolan_kilit_temizlenir_ve_commit_olur():
    import web_app

    eng = _motor()
    gecmis = datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(minutes=1)
    with eng.begin() as c:
        c.execute(
            text("UPDATE users SET locked_until = :t, failed_login_attempts = 9"),
            {"t": gecmis},
        )
    assert web_app._is_account_locked(eng, "u1") is False
    with eng.connect() as c:  # yeni baglanti: commit olmadiysa eski deger doner
        row = c.execute(text("SELECT failed_login_attempts, locked_until FROM users")).mappings().first()
    assert row["locked_until"] is None
    assert row["failed_login_attempts"] == 0


# --- 3. fail-open yok: DB hatasi yutulmaz --------------------------------------
def test_db_hatasi_fail_open_degil():
    import web_app

    eng = create_engine("sqlite://")  # users tablosu yok
    with pytest.raises(Exception):
        web_app._is_account_locked(eng, "u1")


# --- 4. kaynak kod invariantlari ------------------------------------------------
def test_interval_metin_sabiti_kalmadi():
    """Bind parametresi SQL metin sabitinin icine gomulu kalmasin (docstring haric)."""
    kod = re.sub(r'""".*?"""', "", KAYNAK, flags=re.S)
    assert "INTERVAL ':" not in kod


def test_ikiz_fonksiyon_tanimi_yok():
    agac = ast.parse(KAYNAK)
    adlar = [d.name for d in agac.body if isinstance(d, (ast.FunctionDef, ast.AsyncFunctionDef))]
    ikizler = {a for a in adlar if adlar.count(a) > 1}
    assert not ikizler, f"modul duzeyinde ikiz fonksiyon tanimi: {sorted(ikizler)}"


def test_kilit_kontrolu_sifre_dogrulamasindan_once():
    """Kilitli hesap yanlis sifreyle 401 degil 423 almali."""
    govde = KAYNAK[KAYNAK.index("def api_admin_login_post"):]
    govde = govde[: govde.index("\n@app.")]
    i_kilit = govde.index("_is_account_locked(engine")
    i_sifre = govde.index("if not _verify_password(password")
    assert i_kilit < i_sifre, "kilit kontrolu sifre dogrulamasindan sonra kalmis"


if __name__ == "__main__":  # hizli el kontrolu
    raise SystemExit(pytest.main([__file__, "-q"]))
