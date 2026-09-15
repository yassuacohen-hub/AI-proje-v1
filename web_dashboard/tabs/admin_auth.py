"""Admin paneli giriş sekmesi."""
from __future__ import annotations
import os

import streamlit as st
from scripts.dash04_api_client import get_api, APIError


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


def get_admin_token() -> str | None:
    return st.session_state.get("admin_token")


def render_admin_login() -> None:
    st.subheader("Admin Girişi")
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
            # MVP-KUL-FIX-01: API ucu GET + query bekler (web_app.api_admin_login);
            # POST 405 donuyordu ve admin token hic alinamiyordu.
            result = get_api("/api/admin/login", params={"email": email, "password": password})
            if result and result.get("token"):
                st.session_state["admin_token"] = result["token"]
                st.success("Admin olarak giriş yapıldı.")
                st.rerun()
            else:
                st.error("Giriş başarısız: e-posta/şifre kontrol ediniz.")
        except APIError as exc:
            st.error(f"Giriş başarısız: {exc}")


def require_admin_token() -> str | None:
    token = get_admin_token()
    if not token:
        st.info("Admin işlemleri için lütfen giriş yapın.")
    return token
