"""Admin paneli giriş sekmesi (giriş / çıkış / şifre değiştirme)."""
from __future__ import annotations
import os
from pathlib import Path

import streamlit as st
from scripts.dash04_api_client import post_api, APIError

_FLASH_KEY = "_admin_flash"


def _env_kimlik() -> tuple[str, str]:
    """ADMIN-ENV-01: `.env` içindeki ADMIN_EMAIL/ADMIN_PASSWORD ile formu ön-doldurur.

    Değerler yalnızca yerel geliştirme kolaylığı içindir; .env depoya girmez.
    """
    try:  # .env henüz yüklenmemişse (db import edilmeden önce) yükle
        from dotenv import load_dotenv

        load_dotenv(override=False)
    except Exception:
        pass
    return (
        os.getenv("ADMIN_EMAIL", "").strip() or "admin@huginn.local",
        os.getenv("ADMIN_PASSWORD", ""),
    )


def flash_yaz(mesaj: str, tur: str = "success") -> None:
    """ADMIN-RESET-01: `st.rerun()` sonrasında da görünen tek seferlik mesaj kuyruğa alınır."""
    st.session_state[_FLASH_KEY] = {"mesaj": mesaj, "tur": tur}


def flash_goster() -> bool:
    """Bekleyen flash mesajı gösterir ve temizler. Mesaj vardıysa True döner."""
    veri = st.session_state.pop(_FLASH_KEY, None)
    if not veri:
        return False
    tur = veri.get("tur", "success")
    goster = {"success": st.success, "error": st.error, "warning": st.warning}.get(tur, st.info)
    goster(veri.get("mesaj", ""))
    return True


def get_admin_token() -> str | None:
    return st.session_state.get("admin_token")


def _gorunur_bolum_sayisi() -> tuple[int, int]:
    """(admin görünür bölüm, anon görünür bölüm) — giriş sonrası menü büyümesini göstermek için."""
    try:
        from web_dashboard.tabs import ROL_ADMIN, ROL_ANON, gorunur_bolumler

        return len(gorunur_bolumler(ROL_ADMIN)), len(gorunur_bolumler(ROL_ANON))
    except Exception:
        return (0, 0)


def render_admin_login() -> None:
    st.subheader("Admin Girişi")
    flash_goster()
    if get_admin_token():
        # D-24: `/kimlik` sayfası token varken de boş form çiziyordu; sahip girişin
        # gerçekleştiğini anlayamıyordu. Oturum bilgisi + çıkış + menü bilgisi göster.
        render_admin_cikis()
        admin_n, anon_n = _gorunur_bolum_sayisi()
        if admin_n:
            st.info(f"🔓 Oturum açık — sol menüde {admin_n} bölüm görünür (misafir: {anon_n}).")
        return
    env_email, env_sifre = _env_kimlik()
    with st.form("admin_login_form"):
        email = st.text_input("E-posta", value=env_email)
        password = st.text_input("Şifre", type="password", value=env_sifre)
        submitted = st.form_submit_button("Giriş")
    if env_sifre:
        st.caption("🔐 Kimlik `.env` dosyasından ön-dolduruldu (ADMIN_EMAIL / ADMIN_PASSWORD).")
    if submitted:
        st.session_state.pop("admin_token", None)
        try:
            # AUTH-GATE-01: POST /api/admin/login (JSON body).
            result = post_api("/api/admin/login", json={"email": email, "password": password})
            if result and result.get("token"):
                st.session_state["admin_token"] = result["token"]
                st.session_state["admin_email"] = email
                # Mesaj rerun sonrasında gösterilir; aksi halde anında kaybolur.
                flash_yaz(f"✅ Giriş başarılı: {email}")
                st.rerun()
            else:
                st.error("Giriş başarısız: e-posta/şifre kontrol ediniz.")
        except APIError as exc:
            st.error(f"Giriş başarısız: {exc}")
            if "401" in str(exc):
                st.caption(
                    "İpucu: `.env` ADMIN_PASSWORD ile DB şifresi uyuşmuyor olabilir → "
                    "`python scripts/admin_env_eslesme.py` ile kontrol, "
                    "`python scripts/admin_sifre_sifirla.py --env-yaz` ile eşitle."
                )


def admin_cikis() -> None:
    """Oturumu kapatır ve başarı mesajını kuyruğa alır (rerun çağırmaz)."""
    st.session_state.pop("admin_token", None)
    st.session_state.pop("admin_email", None)
    flash_yaz("✅ Çıkış yapıldı. Oturum kapatıldı.")


def render_admin_cikis() -> None:
    """Oturum bilgisi + Çıkış düğmesi (token varken çağrılır)."""
    email = st.session_state.get("admin_email") or "admin"
    col_bilgi, col_btn = st.columns([5, 1])
    with col_bilgi:
        st.caption(f"👤 Oturum açık: **{email}**")
    with col_btn:
        if st.button("🚪 Çıkış", key="admin_cikis_btn", use_container_width=True):
            admin_cikis()
            st.rerun()


def _env_sifre_guncelle(yeni_sifre: str) -> bool:
    """`.env` içindeki ADMIN_PASSWORD değerini günceller (ön-dolum yeni şifreyle uyumlu kalsın)."""
    try:
        from scripts.admin_sifre_sifirla import env_upsert

        env_path = Path(__file__).resolve().parents[2] / ".env"
        env_upsert(env_path, {"ADMIN_PASSWORD": yeni_sifre})
        os.environ["ADMIN_PASSWORD"] = yeni_sifre
        return True
    except Exception:
        return False


def render_sifre_degistir(token: str | None = None) -> None:
    """ADMIN-RESET-01: Oturumdaki admin için şifre değiştirme formu."""
    token = token or get_admin_token()
    if not token:
        st.info("Şifre değiştirmek için önce giriş yapın.")
        return
    with st.form("admin_sifre_degistir_form", clear_on_submit=True):
        mevcut = st.text_input("Mevcut şifre", type="password")
        yeni = st.text_input("Yeni şifre (en az 8 karakter)", type="password")
        tekrar = st.text_input("Yeni şifre (tekrar)", type="password")
        env_guncelle = st.checkbox(
            "`.env` içindeki ADMIN_PASSWORD değerini de güncelle", value=True
        )
        gonder = st.form_submit_button("🔑 Şifreyi değiştir")
    if not gonder:
        return
    if not mevcut or not yeni:
        st.error("Mevcut ve yeni şifre zorunludur.")
        return
    if len(yeni) < 8:
        st.error("Yeni şifre en az 8 karakter olmalı.")
        return
    if yeni != tekrar:
        st.error("Yeni şifreler eşleşmiyor.")
        return
    if yeni == mevcut:
        st.error("Yeni şifre mevcut şifreyle aynı olamaz.")
        return
    try:
        sonuc = post_api(
            "/api/admin/change-password",
            json={"old_password": mevcut, "new_password": yeni},
            token=token,
        )
    except APIError as exc:
        st.error(f"Şifre değiştirilemedi: {exc}")
        return
    if not (sonuc and sonuc.get("ok")):
        st.error("Şifre değiştirilemedi: beklenmeyen yanıt.")
        return
    env_notu = ""
    if env_guncelle:
        env_notu = " `.env` güncellendi." if _env_sifre_guncelle(yeni) else " (.env güncellenemedi.)"
    st.success(f"✅ Şifre başarıyla değiştirildi.{env_notu}")


def require_admin_token() -> str | None:
    token = get_admin_token()
    if not token:
        st.info("Admin işlemleri için lütfen giriş yapın.")
    return token
