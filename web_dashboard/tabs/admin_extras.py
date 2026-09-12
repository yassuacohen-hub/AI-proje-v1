"""Admin Panel API ve Kullanici yonetimi sekmesi."""
from __future__ import annotations
from typing import Any
import pandas as pd
import streamlit as st
from scripts.dash04_api_client import get_api, APIError


def render_api_management() -> None:
    st.subheader("API Yönetimi")
    try:
        data = get_api("/api/admin/api-usage")
        if isinstance(data, dict):
            items = data.get("items", [])
            limits = data.get("rate_limits", {})
            if items:
                st.dataframe(pd.DataFrame(items), use_container_width=True, hide_index=True)
            else:
                st.info("API kullanım kaydı yok.")
            if limits:
                st.json(limits)
    except APIError as exc:
        st.warning(f"API Yönetimi yüklenemedi: {exc}")


def render_user_management() -> None:
    st.subheader("Kullanıcı Yönetimi")
    try:
        pending = get_api("/api/admin/pending")
        categories = get_api("/api/admin/categories")
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
    except APIError as exc:
        st.warning(f"Kullanıcı Yönetimi yüklenemedi: {exc}")
