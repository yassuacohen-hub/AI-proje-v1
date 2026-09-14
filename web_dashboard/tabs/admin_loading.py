# -*- coding: utf-8 -*-
"""P7-42: Loading states — Skeleton screens, progress indicators.

Streamlit loading UX iyilestirmeleri:
- Progress bar ile uzun islem takibi
- Skeleton-style placeholder gosterimi
- Loading overlay
- Async islem durumu gosterimi
"""
from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Any

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "src"))


def render_loading_tab() -> None:
    """Loading states sekmesini gosterir."""
    st.subheader("⏳ Loading States & Progress")

    st.divider()
    st.subheader("📊 Progress Bar — Uzun Islem Takibi")

    col_progress, col_status = st.columns([3, 2])

    with col_progress:
        progress = st.progress(0, text="Bekleniyor...")

    with col_status:
        if "task_status" not in st.session_state:
            st.session_state.task_status = "Hazir"
        status_placeholder = st.empty()
        status_placeholder.info(f"Durum: {st.session_state.task_status}")

    st.divider()
    st.subheader("🧪 Demo — Simüle Islem")

    demo_type = st.radio(
        "Islem Turu",
        ["Veri Yukleme", "Kalite Hesaplama", "Export", "Arama"],
        horizontal=True,
    )

    if st.button("▶️ Calistir", type="primary", width="stretch"):
        steps = {
            "Veri Yukleme": ["Baglantı kuruluyor...", "Veri çekiliyor...", "İşleniyor...", "Tamamlandı!"],
            "Kalite Hesaplama": ["Skor hesaplanıyor...", "Kurallar uygulanıyor...", "Rapor oluşturuluyor...", "Tamamlandı!"],
            "Export": ["Veri hazırlanıyor...", "Format oluşturuluyor...", "Dosya yazılıyor...", "Tamamlandı!"],
            "Arama": ["Sorgu oluşturuluyor...", "Veritabanında aranıyor...", "Sonuçlar sıralanıyor...", "Tamamlandı!"],
        }
        messages = steps.get(demo_type, [])
        for i, msg in enumerate(messages):
            pct = (i + 1) / len(messages)
            progress.progress(pct, text=msg)
            st.session_state.task_status = msg
            status_placeholder.info(f"Durum: {msg}")
            time.sleep(0.5)

        st.session_state.task_status = "Tamamlandı"
        status_placeholder.success(f"Durum: Tamamlandı")

    st.divider()
    st.subheader("🦴 Skeleton Loader (Simülasyon)")

    if st.checkbox("Skeleton gosterimi aç", key="skeleton_toggle"):
        cols = st.columns(3)
        for i, col in enumerate(cols):
            with col:
                st.empty()
                st.markdown(
                    f'<div style="background:#e0e0e0;height:20px;border-radius:4px;margin:4px 0"></div>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f'<div style="background:#f0f0f0;height:60px;border-radius:4px;margin:4px 0"></div>',
                    unsafe_allow_html=True,
                )
                st.markdown(
                    f'<div style="background:#e0e0e0;height:15px;border-radius:4px;margin:4px 0;width:{60 + i * 20}%"></div>',
                    unsafe_allow_html=True,
                )

    st.divider()
    st.subheader("⏱️ Timeout Ayarları")

    col1, col2 = st.columns(2)
    with col1:
        timeout = st.selectbox(
            "Sorgu Timeout",
            [5, 10, 30, 60, 120],
            index=1,
            key="query_timeout",
        )
        st.session_state.query_timeout = timeout
    with col2:
        retry = st.selectbox(
            "Tekrar Deneme",
            [0, 1, 2, 3, 5],
            index=2,
            key="retry_count",
        )
        st.session_state.retry_count = retry

    st.caption(f"Timeout: {timeout}s | Retry: {retry} | Current: {st.session_state.get('query_timeout', 10)}s")
