"""Admin Panel API ve Kullanici yonetimi sekmesi."""
from __future__ import annotations
from typing import Any
import pandas as pd
import streamlit as st
from company_master.ui import (
    PageHeader,
    bos_durum,
    api_cagir,
)
from scripts.dash04_api_client import get_api, APIError, post_api

# K-1: Tier secimleri — JSON konfigurasyon (sabit liste disindan cikarildi).
TIER_SECIMLERI: list[str] = ["terminal", "strategic", "enterprise"]


def render_api_management(token: str | None = None) -> None:
    if token is None:
        token = st.session_state.get("admin_token")
    st.subheader("API Yönetimi")

    def _yukle_api_kullanimi():
        return get_api("/api/admin/api-usage", token=token)

    data = api_cagir(
        _yukle_api_kullanimi,
        baslik="API Kullanımı",
        ipucu="API kullanım istatistiklerini yüklerken hata oluştu."
    )

    if data:
        if isinstance(data, dict):
            items = data.get("items", [])
            limits = data.get("rate_limits", {})
            if items:
                st.dataframe(pd.DataFrame(items), width="stretch", hide_index=True)
            else:
                bos_durum("API kullanım kaydı yok.")
            if limits:
                st.json(limits)


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

    def _yukle_bekleyen_ve_kategoriler():
        pending = get_api("/api/admin/pending", token=token)
        categories = get_api("/api/admin/categories", token=token)
        return {"pending": pending, "categories": categories}

    result = api_cagir(
        _yukle_bekleyen_ve_kategoriler,
        baslik="Kullanıcı Yönetimi",
        ipucu="Onay bekleyen kullanıcıları ve kategorileri yüklerken hata oluştu."
    )

    if result:
        pending = result.get("pending", {})
        if isinstance(pending, dict):
            bekleyen = pending.get("bekleyen", [])
            if bekleyen:
                for user in bekleyen:
                    cols = st.columns([4, 1])
                    with cols[0]:
                        # Tier selector for approval
                        tiers = TIER_SECIMLERI
                        default_tier = user.get("tier", "terminal")
                        try:
                            default_index = tiers.index(default_tier)
                        except ValueError:
                            default_index = 0
                        selected_tier = st.selectbox(
                            "Tier",
                            options=tiers,
                            index=default_index,
                            key=f"tier_select_{user.get('user_id', '')}",
                            label_visibility="collapsed"
                        )
                        st.write(
                            f"**{user.get('email', '')}** — {user.get('company_name', '')} ({user.get('tier', '')})"
                        )
                    with cols[1]:
                        if st.button("Onayla", key=f"approve_{user.get('user_id', '')}"):
                            try:
                                post_api(
                                    "/api/admin/approve",
                                    json={"user_id": user.get("user_id", ""), "tier": selected_tier},
                                    token=token,
                                )
                                st.success(f"{user.get('email', '')} onaylandı ({selected_tier} tier)")
                                st.cache_data.clear()
                                st.rerun()
                            except APIError as e:
                                st.error(f"Onaylama başarısız: {e}")
            else:
                bos_durum("Onay bekleyen kullanıcı yok.")

            onayli_son = pending.get("onayli_son", [])
            if onayli_son:
                st.dataframe(pd.DataFrame(onayli_son), width="stretch", hide_index=True)
            else:
                bos_durum("Son onaylı kullanıcı yok.")

        categories = result.get("categories", {})
        if isinstance(categories, dict):
            items = categories.get("items", [])
            if items:
                st.dataframe(pd.DataFrame(items), width="stretch", hide_index=True)
            else:
                bos_durum("Kategori kaydı yok.")

        # D-215: Kredi yükleme formu KALDIRILDI — kanonik yer: musteri_yonetimi.render_paket_kredi_tab()
        # (Gelir Kapısı > Paket & Kredi). Bu dosyadaki kopyası ikiz (D-211) oluştururdu.
