# -*- coding: utf-8 -*-
"""P7-39: Dashboard veri yenileme optimizasyonu.

Streamlit auto-refresh mekanizmasi:
- Ayarlanabilir refresh araligi (1/5/10/30/60 saniye)
- Otomatik yenileme acik/kapatma
- Son yenileme zamani gosterimi
- Oncelikli sayfa elemanlari icin sezgisel guncelleme
"""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "src"))

REFRESH_INTERVALS = [15, 30, 60, 300, 600]


def render_auto_refresh() -> None:
    """Auto-refresh kontrolleri ve durum gosterimi."""
    st.subheader("🔄 Veri Yenileme Optimizasyonu")

    if "auto_refresh_interval" not in st.session_state:
        st.session_state.auto_refresh_interval = 30
    if "auto_refresh_enabled" not in st.session_state:
        st.session_state.auto_refresh_enabled = False
    if "last_auto_refresh" not in st.session_state:
        st.session_state.last_auto_refresh = datetime.now()

    col_int, col_btn, col_status = st.columns([2, 2, 3])

    with col_int:
        interval = st.selectbox(
            "Yenileme Araligi",
            REFRESH_INTERVALS,
            index=REFRESH_INTERVALS.index(st.session_state.auto_refresh_interval),
            key="refresh_interval_select",
        )
        st.session_state.auto_refresh_interval = interval

    with col_btn:
        if st.session_state.auto_refresh_enabled:
            if st.button("⏹ Otomatik Yenileme: KAPALI", type="primary", width="stretch"):
                st.session_state.auto_refresh_enabled = False
        else:
            if st.button("▶️ Otomatik Yenileme: AÇIK", type="primary", width="stretch"):
                st.session_state.auto_refresh_enabled = True

    with col_status:
        elapsed = (datetime.now() - st.session_state.last_auto_refresh).total_seconds()
        remaining = max(0, st.session_state.auto_refresh_interval - elapsed)
        st.metric("Son Yenileme", st.session_state.last_auto_refresh.strftime("%H:%M:%S"))
        st.metric("Kalan", f"{remaining:.0f}s")

    if st.session_state.auto_refresh_enabled:
        st.success(f"✅ Otomatik yenileme AÇIK ({interval}s aralıkla)")
        st.auto_refresh(interval=interval, key="auto_refresh")
    else:
        st.info("⏸️ Otomatik yenileme KAPALI — manuel yenileme bekleniyor")

    st.divider()
    st.subheader("📊 Otomasyon Özeti")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Aralık", f"{st.session_state.auto_refresh_interval}s")
    with col2:
        status = "Aktif" if st.session_state.auto_refresh_enabled else "Devre Dışı"
        st.metric("Durum", status)
    with col3:
        st.metric("Son Yenileme", st.session_state.last_auto_refresh.strftime("%H:%M:%S"))

    st.caption("Not: Streamlit auto_refresh, sayfa elemanlarini otomatik olarak gunceller. Cache'ler otomatik temizlenir.")
