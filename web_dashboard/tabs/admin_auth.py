"""Admin paneli giriş sekmesi."""
from __future__ import annotations
import streamlit as st
from scripts.dash04_api_client import post_api, APIError


def get_admin_token() -> str | None:
    return st.session_state.get("admin_token")


def render_admin_login() -> None:
    st.subheader("Admin Girişi")
    with st.form("admin_login_form"):
        email = st.text_input("E-posta", value="admin@huginn.local")
        password = st.text_input("Şifre", type="password")
        submitted = st.form_submit_button("Giriş")
    if submitted:
        try:
            result = post_api("/api/admin/login", json={"email": email, "password": password})
            if result and result.get("token"):
                st.session_state["admin_token"] = result["token"]
                st.success("Admin olarak giriş yapıldı.")
                st.rerun()
            else:
                st.error("Giriş başarısız: token alınamadı.")
        except APIError as exc:
            st.error(f"Giriş hata: {exc}")


def require_admin_token() -> str | None:
    token = get_admin_token()
    if not token:
        st.info("Admin işlemleri için lütfen giriş yapın.")
    return token
