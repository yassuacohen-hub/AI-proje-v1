# -*- coding: utf-8 -*-
"""ADMIN-RESET-01: giriş/çıkış flash mesajı + admin şifre değiştirme testleri."""
from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from scripts.dash04_api_client import APIError
from web_dashboard.tabs import admin_auth


# ---------------------------------------------------------------- flash mekanizması
def test_flash_yaz_ve_goster_tek_seferlik(monkeypatch):
    state: dict = {}
    monkeypatch.setattr(admin_auth.st, "session_state", state)
    success = MagicMock()
    monkeypatch.setattr(admin_auth.st, "success", success)

    admin_auth.flash_yaz("merhaba")
    assert admin_auth.flash_goster() is True
    success.assert_called_once_with("merhaba")
    # ikinci çağrıda mesaj yok (temizlenmiş)
    assert admin_auth.flash_goster() is False
    assert admin_auth._FLASH_KEY not in state


def test_flash_goster_tur_error(monkeypatch):
    monkeypatch.setattr(admin_auth.st, "session_state", {})
    error = MagicMock()
    monkeypatch.setattr(admin_auth.st, "error", error)
    admin_auth.flash_yaz("hata", tur="error")
    admin_auth.flash_goster()
    error.assert_called_once_with("hata")


# ---------------------------------------------------------------- giriş mesajı
def test_giris_basarili_flash_kuyruga_alinir_ve_rerun(monkeypatch):
    """st.success hemen rerun ile kayboluyordu; artık flash kuyruğuna yazılır."""
    state: dict = {}
    monkeypatch.setattr(admin_auth.st, "session_state", state)
    monkeypatch.setattr(admin_auth.st, "form", lambda *a, **k: MagicMock())
    monkeypatch.setattr(admin_auth.st, "text_input", lambda *a, **k: "admin@huginn.local")
    monkeypatch.setattr(admin_auth.st, "form_submit_button", lambda *a, **k: True)
    monkeypatch.setattr(admin_auth.st, "caption", MagicMock())
    rerun = MagicMock()
    monkeypatch.setattr(admin_auth.st, "rerun", rerun)
    monkeypatch.setattr(admin_auth, "post_api", lambda *a, **k: {"token": "tok-1"})

    admin_auth.render_admin_login()

    assert state["admin_token"] == "tok-1"
    assert state["admin_email"] == "admin@huginn.local"
    assert state[admin_auth._FLASH_KEY]["tur"] == "success"
    assert "Giriş başarılı" in state[admin_auth._FLASH_KEY]["mesaj"]
    rerun.assert_called_once()


# ---------------------------------------------------------------- çıkış
def test_admin_cikis_token_siler_ve_flash_yazar(monkeypatch):
    state = {"admin_token": "tok", "admin_email": "a@b.c"}
    monkeypatch.setattr(admin_auth.st, "session_state", state)

    admin_auth.admin_cikis()

    assert "admin_token" not in state
    assert "admin_email" not in state
    assert "_force_auth_gate" not in state
    assert "Çıkış yapıldı" in state[admin_auth._FLASH_KEY]["mesaj"]


def test_render_admin_cikis_butona_basinca_rerun(monkeypatch):
    state = {"admin_token": "tok", "admin_email": "a@b.c"}
    monkeypatch.setattr(admin_auth.st, "session_state", state)
    kolon = MagicMock()
    kolon.__enter__ = lambda s: s
    kolon.__exit__ = lambda s, *a: False
    monkeypatch.setattr(admin_auth.st, "columns", lambda *a, **k: (kolon, kolon))
    monkeypatch.setattr(admin_auth.st, "caption", MagicMock())
    monkeypatch.setattr(admin_auth.st, "button", lambda *a, **k: True)
    rerun = MagicMock()
    monkeypatch.setattr(admin_auth.st, "rerun", rerun)

    admin_auth.render_admin_cikis()

    assert "admin_token" not in state
    rerun.assert_called_once()


# ---------------------------------------------------------------- şifre değiştir (UI)
def _sifre_formu_hazirla(monkeypatch, girdiler: list[str]):
    state = {"admin_token": "tok"}
    monkeypatch.setattr(admin_auth.st, "session_state", state)
    monkeypatch.setattr(admin_auth.st, "form", lambda *a, **k: MagicMock())
    sirali = iter(girdiler)
    monkeypatch.setattr(admin_auth.st, "text_input", lambda *a, **k: next(sirali))
    monkeypatch.setattr(admin_auth.st, "form_submit_button", lambda *a, **k: True)
    error = MagicMock()
    success = MagicMock()
    monkeypatch.setattr(admin_auth.st, "error", error)
    monkeypatch.setattr(admin_auth.st, "success", success)
    return state, error, success


def test_sifre_degistir_token_yoksa_info(monkeypatch):
    monkeypatch.setattr(admin_auth.st, "session_state", {})
    info = MagicMock()
    monkeypatch.setattr(admin_auth.st, "info", info)
    admin_auth.render_sifre_degistir()
    info.assert_called_once()


@pytest.mark.parametrize(
    "girdiler, beklenen",
    [
        (["eski1234", "kisa", "kisa"], "en az 8"),
        (["eski1234", "yeni12345", "farkli123"], "eşleşmiyor"),
        (["ayni1234", "ayni1234", "ayni1234"], "aynı olamaz"),
        (["", "yeni12345", "yeni12345"], "zorunludur"),
    ],
)
def test_sifre_degistir_yerel_dogrulama(monkeypatch, girdiler, beklenen):
    _, error, success = _sifre_formu_hazirla(monkeypatch, girdiler)
    post = MagicMock()
    monkeypatch.setattr(admin_auth, "post_api", post)

    admin_auth.render_sifre_degistir()

    post.assert_not_called()
    success.assert_not_called()
    assert beklenen in error.call_args[0][0]


def test_sifre_degistir_basarili_post_ve_success(monkeypatch):
    """D-194: checkbox kaldırıldı — .env her zaman sessizce güncellenir."""
    _, error, success = _sifre_formu_hazirla(monkeypatch, ["eski1234", "yeni12345", "yeni12345"])
    cagri: dict = {}

    def sahte_post(endpoint, json=None, token=None, **kwargs):
        cagri.update(endpoint=endpoint, json=json, token=token)
        return {"ok": True}

    monkeypatch.setattr(admin_auth, "post_api", sahte_post)
    env = MagicMock(return_value=True)
    monkeypatch.setattr(admin_auth, "_env_sifre_guncelle", env)

    admin_auth.render_sifre_degistir()

    assert cagri["endpoint"] == "/api/admin/change-password"
    assert cagri["json"] == {"old_password": "eski1234", "new_password": "yeni12345"}
    assert cagri["token"] == "tok"
    env.assert_called_once_with("yeni12345")
    error.assert_not_called()
    assert "başarıyla" in success.call_args[0][0]
    assert "`.env` güncellendi" in success.call_args[0][0]


def test_sifre_degistir_api_hatasi(monkeypatch):
    _, error, success = _sifre_formu_hazirla(monkeypatch, ["eski1234", "yeni12345", "yeni12345"])
    monkeypatch.setattr(
        admin_auth, "post_api", lambda *a, **k: (_ for _ in ()).throw(APIError("mevcut sifre hatali"))
    )

    admin_auth.render_sifre_degistir()

    success.assert_not_called()
    assert "mevcut sifre hatali" in error.call_args[0][0]


def test_env_sifre_guncelle_env_upsert_cagirir(monkeypatch, tmp_path):
    import scripts.admin_sifre_sifirla as ass

    yazilan: dict = {}
    monkeypatch.setattr(ass, "env_upsert", lambda p, d: yazilan.update(d))
    monkeypatch.delenv("ADMIN_PASSWORD", raising=False)

    assert admin_auth._env_sifre_guncelle("yeni12345") is True
    assert yazilan == {"ADMIN_PASSWORD": "yeni12345"}
    import os

    assert os.environ["ADMIN_PASSWORD"] == "yeni12345"


# ---------------------------------------------------------------- API ucu (web_app)
@pytest.fixture
def web_app_mod():
    pytest.importorskip("fastapi")
    import web_app

    return web_app


class _Conn:
    def __init__(self, hash_):
        self.hash_ = hash_
        self.updates: list = []

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False

    def execute(self, sql, params=None):
        s = str(sql)
        if s.strip().upper().startswith("UPDATE"):
            self.updates.append(params)
            return MagicMock()
        m = MagicMock()
        m.mappings.return_value.first.return_value = {"password_hash": self.hash_}
        return m


class _Engine:
    def __init__(self, hash_):
        self.conn = _Conn(hash_)

    def connect(self):
        return self.conn

    def begin(self):
        return self.conn


def _admin(role="admin", status="onayli"):
    return {"user_id": "u1", "email": "admin@huginn.local", "role": role, "status": status}


def test_api_change_password_basarili(monkeypatch, web_app_mod):
    from fastapi import HTTPException  # noqa: F401

    eski_hash = web_app_mod._hash_password("eski1234")
    engine = _Engine(eski_hash)
    monkeypatch.setattr(web_app_mod, "get_engine", lambda: engine)
    monkeypatch.setattr(web_app_mod, "_user_from_token", lambda t: _admin() if t == "tok" else None)
    req = MagicMock()
    req.headers = {}

    out = web_app_mod.api_admin_change_password(
        {"old_password": "eski1234", "new_password": "yeni12345"}, req, token="tok"
    )

    assert out["ok"] is True
    assert len(engine.conn.updates) == 1
    yeni_hash = engine.conn.updates[0]["p"]
    assert web_app_mod._verify_password("yeni12345", yeni_hash)


def test_api_change_password_bearer_header(monkeypatch, web_app_mod):
    engine = _Engine(web_app_mod._hash_password("eski1234"))
    monkeypatch.setattr(web_app_mod, "get_engine", lambda: engine)
    monkeypatch.setattr(web_app_mod, "_user_from_token", lambda t: _admin() if t == "tok" else None)
    req = MagicMock()
    req.headers = {"Authorization": "Bearer tok"}

    out = web_app_mod.api_admin_change_password(
        {"old_password": "eski1234", "new_password": "yeni12345"}, req
    )
    assert out["ok"] is True


@pytest.mark.parametrize(
    "user, body, kod",
    [
        (None, {"old_password": "eski1234", "new_password": "yeni12345"}, 403),
        (_admin(role="buyer"), {"old_password": "eski1234", "new_password": "yeni12345"}, 403),
        (_admin(status="beklemede"), {"old_password": "eski1234", "new_password": "yeni12345"}, 403),
        (_admin(), {"old_password": "eski1234", "new_password": "kisa"}, 400),
        (_admin(), {"old_password": "", "new_password": "yeni12345"}, 400),
        (_admin(), {"old_password": "eski1234", "new_password": "eski1234"}, 400),
        (_admin(), {"old_password": "yanlis999", "new_password": "yeni12345"}, 401),
    ],
)
def test_api_change_password_hatalar(monkeypatch, web_app_mod, user, body, kod):
    from fastapi import HTTPException

    engine = _Engine(web_app_mod._hash_password("eski1234"))
    monkeypatch.setattr(web_app_mod, "get_engine", lambda: engine)
    monkeypatch.setattr(web_app_mod, "_user_from_token", lambda t: user)
    req = MagicMock()
    req.headers = {}

    with pytest.raises(HTTPException) as ei:
        web_app_mod.api_admin_change_password(body, req, token="tok")
    assert ei.value.status_code == kod
    assert engine.conn.updates == []
