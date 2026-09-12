"""Admin Panel API ve Kullanici yonetimi sekmesi."""
from __future__ import annotations
from typing import Any
import pandas as pd
import streamlit as st
from scripts.dash04_api_client import get_api, APIError


def render_api_management(token: str | None = None) -> None:
    if token is None:
        token = st.session_state.get("admin_token")
    st.subheader("API Yönetimi")
    try:
        data = get_api("/api/admin/api-usage", token=token)
        if isinstance(data, dict):
            items = data.get("items", [])
            limits = data.get("rate_limits", {})
            if items:
                st.dataframe(pd.DataFrame(items), use_container_width=True, hide_index=True)
            else:
                st.info("API kullanım kaydı yok.")
            if limits:
                st.json(limits)
    except APIError:
        st.warning("Lütfen giriş yapın veya yetkili olun")


def render_user_management(token: str | None = None) -> None:
    if token is None:
        token = st.session_state.get("admin_token")
    st.subheader("Kullanıcı Yönetimi")
    try:
        pending = get_api("/api/admin/pending", token=token)
        categories = get_api("/api/admin/categories", token=token)
        if isinstance(pending, dict):
            for key, label in [("bekleyen", "Onay Bekleyen Kullanıcılar"), ("onayli_son", "Son Onaylı Kullanıcılar")]:
                rows = pending.get(key, [])
                if rows:
                    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
                else:
                    st.info(f"{label}: yok")
        if isinstance(categories, dict):
            items = categories.get("items", [])
            if items:
                st.dataframe(pd.DataFrame(items), use_container_width=True, hide_index=True)
            else:
                st.info("Kategori kaydı yok.")
    except APIError:
        st.warning("Lütfen giriş yapın veya yetkili olun")

