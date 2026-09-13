"""Birlesik Yonetim sekmesi.

API/kullanici yonetimi, export, global arama ve otomatik yenileme panellerini
tek operasyonel yonetim gorunumunde toplar. Alt moduller kendi veri akislarini
ve aksiyonlarini korur.
"""
from __future__ import annotations

from datetime import datetime

import streamlit as st

from web_dashboard.tabs.admin_auto_refresh import render_auto_refresh
from web_dashboard.tabs.admin_extras import render_api_management, render_user_management
from web_dashboard.tabs.admin_export import render_export_tab
from web_dashboard.tabs.admin_search import render_search_tab


def render_yonetim_tab() -> None:
    """Yonetim panellerini tek sekmede render eder."""
    st.subheader("🛠️ Yönetim")
    st.caption(
        "API, kullanici, export, arama ve yenileme ayarlari · "
        f"Son guncelleme: {datetime.now().strftime('%H:%M')}"
    )

    if st.button("🔄 Yönetim verilerini yenile", key="yonetim-refresh"):
        st.cache_data.clear()
        st.rerun()

    st.info(
        "Bu sekme yonetim ve operasyon ayarlarini toplar. Yetki gerektiren "
        "islemler icin admin girisi gerekir."
    )

    st.divider()
    st.subheader("API ve Kullanıcı Yönetimi")
    render_api_management(token=st.session_state.get("admin_token"))
    render_user_management(token=st.session_state.get("admin_token"))

    st.divider()
    st.subheader("Veri Araçları")
    render_search_tab()
    render_export_tab()

    st.divider()
    st.subheader("Otomatik Yenileme")
    render_auto_refresh()
