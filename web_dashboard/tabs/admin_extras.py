"""Admin Panel API ve Kullanici yonetimi sekmesi."""
from __future__ import annotations
from typing import Any
import pandas as pd
import streamlit as st
from company_master.ui import PageHeader
from scripts.dash04_api_client import get_api, APIError, post_api


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
                st.dataframe(pd.DataFrame(items), width="stretch", hide_index=True)
            else:
                st.info("API kullanım kaydı yok.")
            if limits:
                st.json(limits)
    except APIError:
        st.warning("Lütfen giriş yapın veya yetkili olun")


def render_user_management(token: str | None = None) -> None:
    if token is None:
        token = st.session_state.get("admin_token")
    PageHeader(
        "Kullanıcı Yönetimi",
        "Onay bekleyen kullanıcıları yönetin ve kredi paketi tanımlayın.",
        ust_etiket="İş · Yönetim",
        ikon="👥",
    ).render()
    if not token:
        st.warning("Lütfen giriş yapın")
        return
    try:
        pending = get_api("/api/admin/pending", token=token)
        if isinstance(pending, dict):
            bekleyen = pending.get("bekleyen", [])
            if bekleyen:
                for user in bekleyen:
                    cols = st.columns([4, 1])
                    with cols[0]:
                        st.write(
                            f"**{user.get('email', '')}** — {user.get('company_name', '')} ({user.get('tier', '')})"
                        )
                    with cols[1]:
                        if st.button("Onayla", key=f"approve_{user.get('user_id', '')}"):
                            try:
                                post_api(
                                    "/api/admin/approve",
                                    json={"user_id": user.get("user_id", ""), "tier": "terminal"},
                                    token=token,
                                )
                                st.success(f"{user.get('email', '')} onaylandı")
                                st.cache_data.clear()
                                st.rerun()
                            except APIError as e:
                                st.error(f"Onaylama başarısız: {e}")
            else:
                st.info("Onay bekleyen kullanıcı yok.")

            onayli_son = pending.get("onayli_son", [])
            if onayli_son:
                st.dataframe(pd.DataFrame(onayli_son), width="stretch", hide_index=True)
            else:
                st.info("Son onaylı kullanıcı yok.")

        categories = get_api("/api/admin/categories", token=token)
        if isinstance(categories, dict):
            items = categories.get("items", [])
            if items:
                st.dataframe(pd.DataFrame(items), width="stretch", hide_index=True)
            else:
                st.info("Kategori kaydı yok.")

        with st.form("kredi_formu"):
            col1, col2 = st.columns(2)
            with col1:
                kredi_user_id = st.text_input("Kullanıcı ID")
            with col2:
                kredi_miktar = st.number_input("Kredi Miktarı", min_value=1, value=50)
            if st.form_submit_button("Kredi Yükle") and kredi_user_id:
                try:
                    post_api(
                        "/api/admin/credit",
                        json={"user_id": kredi_user_id, "amount": kredi_miktar},
                        token=token,
                    )
                    st.success(f"{kredi_miktar} kredi yüklendi.")
                    st.cache_data.clear()
                    st.rerun()
                except APIError as e:
                    st.error(f"Kredi yükleme başarısız: {e}")
    except APIError:
        st.warning("Lütfen giriş yapın veya yetkili olun")