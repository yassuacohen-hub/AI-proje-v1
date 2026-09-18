# -*- coding: utf-8 -*-
"""ADMIN-SIFRE-RESET-FLOW-01: giriş ekranı 'Şifremi unuttum' akışı.

KAHİN bulgusu: "şifremi unuttum çalısmıyor". Kök neden: API uçları
(`/api/admin/reset-request`, `/api/admin/reset-confirm`) hazırdı ama UI'da
karşılığı yoktu. Bu test köprünün geri gitmesini engeller.
"""
from unittest.mock import MagicMock

from web_dashboard.tabs import admin_auth


def _ui_hazirla(monkeypatch, state: dict, metin: str = "kod12345678") -> None:
    """expander/form/text_input/submit sahteleri — iki form da tıklanmış sayılır."""
    monkeypatch.setattr(admin_auth.st, "session_state", state)
    monkeypatch.setattr(admin_auth.st, "expander", lambda *a, **k: MagicMock())
    monkeypatch.setattr(admin_auth.st, "form", lambda *a, **k: MagicMock())
    monkeypatch.setattr(admin_auth.st, "text_input", lambda *a, **k: metin)
    monkeypatch.setattr(admin_auth.st, "form_submit_button", lambda *a, **k: True)
    for ad in ("caption", "success", "error", "rerun"):
        monkeypatch.setattr(admin_auth.st, ad, MagicMock())


def test_iki_api_ucu_dogru_govde_ile_cagrilir(monkeypatch):
    state: dict = {}
    _ui_hazirla(monkeypatch, state)
    cagrilar: list[tuple[str, dict]] = []
    monkeypatch.setattr(
        admin_auth,
        "post_api",
        lambda endpoint, json=None, **k: (cagrilar.append((endpoint, json)), {"ok": True})[1],
    )

    admin_auth.render_sifre_unuttum()

    assert cagrilar[0] == ("/api/admin/reset-request", {"email": "kod12345678"})
    assert cagrilar[1] == (
        "/api/admin/reset-confirm",
        {"email": "kod12345678", "token": "kod12345678", "new_password": "kod12345678"},
    )
    assert state[admin_auth._FLASH_KEY]["mesaj"].startswith("✅")


def test_kisa_sifre_api_cagirmaz(monkeypatch):
    """Sunucuya gitmeden önce istemci tarafı en az 8 karakter kontrolü."""
    state: dict = {}
    _ui_hazirla(monkeypatch, state, metin="kisa")
    cagrilar: list[str] = []
    monkeypatch.setattr(
        admin_auth,
        "post_api",
        lambda endpoint, json=None, **k: (cagrilar.append(endpoint), {"ok": True})[1],
    )

    admin_auth.render_sifre_unuttum()

    assert cagrilar == ["/api/admin/reset-request"]  # onay ucu çağrılmadı
    admin_auth.st.error.assert_called_with("Yeni şifre en az 8 karakter olmalı.")


def test_api_hatasi_genel_mesajla_gizlenir(monkeypatch):
    """SEC-AUTH-01 Y-2: sunucu detayı kullanıcıya sızmaz."""
    state: dict = {}
    _ui_hazirla(monkeypatch, state)
    monkeypatch.setattr(
        admin_auth,
        "post_api",
        lambda *a, **k: (_ for _ in ()).throw(admin_auth.APIError("token expired")),
    )

    admin_auth.render_sifre_unuttum()

    mesajlar = [c.args[0] for c in admin_auth.st.error.call_args_list]
    assert not any("token expired" in m for m in mesajlar)


def test_giris_ekranindan_cagriliyor(monkeypatch):
    """Akış giriş formunun altında gerçekten çiziliyor."""
    state: dict = {}
    monkeypatch.setattr(admin_auth.st, "session_state", state)
    monkeypatch.setattr(admin_auth.st, "form", lambda *a, **k: MagicMock())
    monkeypatch.setattr(admin_auth.st, "text_input", lambda *a, **k: "admin@huginn.local")
    monkeypatch.setattr(admin_auth.st, "form_submit_button", lambda *a, **k: False)
    monkeypatch.setattr(admin_auth.st, "subheader", MagicMock())
    monkeypatch.setattr(admin_auth.st, "caption", MagicMock())
    cagrildi = MagicMock()
    monkeypatch.setattr(admin_auth, "render_sifre_unuttum", cagrildi)

    admin_auth.render_admin_login()

    cagrildi.assert_called_once()
