"""Birlesik Sistem sekmesi.

Maliyet, performans, API analitigi, DLQ ve webhook izlemeyi tek operasyonel
sistem gorunumunde toplar. Veri yukleme ve alt sekme davranislari mevcut
modullerde tutulur.
"""
from __future__ import annotations

from datetime import datetime

import streamlit as st

from web_dashboard.tabs.admin_api_analytics import render_api_analytics_tab
from web_dashboard.tabs.admin_cost import render_cost_tab
from web_dashboard.tabs.admin_dlq import render_dlq_tab
from web_dashboard.tabs.admin_performance import render_performance_tab
from web_dashboard.tabs.webhook_monitor import render_webhook_monitor_tab


def render_sistem_tab() -> None:
    """Tum sistem operasyon panellerini tek sekmede render eder."""
    st.subheader("⚙️ Sistem")
    st.caption(
        "Maliyet, performans, API kullanimi, DLQ ve webhook sagligi · "
        f"Son guncelleme: {datetime.now().strftime('%H:%M')}"
    )

    st.info(
        "Bu sekme platform sagligini izler. Bos paneller, ilgili veri kaynagi "
        "ilk kez veri urettiginde otomatik olarak dolacaktir."
    )

    if st.button("🔄 Sistem verilerini yenile", key="sistem-refresh"):
        st.cache_data.clear()
        st.rerun()

    st.divider()
    st.subheader("Webhook ve DLQ")
    render_webhook_monitor_tab()
    render_dlq_tab()

    st.divider()
    st.subheader("Performans ve Maliyet")
    render_performance_tab()
    render_cost_tab()

    st.divider()
    st.subheader("API Analitigi")
    render_api_analytics_tab()
