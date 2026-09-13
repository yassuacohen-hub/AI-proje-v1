"""Musteriler ekrani: firma listesi, filtreler ve operasyon bildirimleri."""
from __future__ import annotations

from datetime import datetime

import pandas as pd
import streamlit as st

from web_dashboard.tabs.admin_kpi import load_admin_kpi_summary
from web_dashboard.tabs.admin_search import get_source_names, search_companies


def render_musteriler_tab() -> None:
    """Firma listesini filtreler ve kritik kalite bildirimlerini gosterir."""
    st.subheader("👥 Müşteriler")
    st.caption("Firma listesi ve kalite görünümü · Son güncelleme: " + datetime.now().strftime("%H:%M"))

    kpi = load_admin_kpi_summary()
    if kpi:
        st.info(
            f"Bildirim: {kpi.get('son_24s_yeni_firma', 0)} yeni firma, "
            f"{kpi.get('sinyal_toplam', 0)} toplam sinyal. "
            "Kalitesi düşük firmaları filtreleyerek inceleyin."
        )
    else:
        st.info("Bildirim verisi henüz hazır değil; firma verisi geldiğinde burada görünecek.")

    col_query, col_score = st.columns([3, 2])
    with col_query:
        query = st.text_input("🔍 Firma ara", placeholder="Unvan, VKN, telefon, e-posta veya NACE", key="musteriler-query")
    with col_score:
        score_range = st.slider("Kalite skoru", 0, 100, (0, 100), key="musteriler-score")

    sources = get_source_names()
    source = st.selectbox("Kaynak", ["Tümü"] + sources, key="musteriler-source")
    limit = st.selectbox("Gösterilecek firma", [50, 100, 200], key="musteriler-limit")

    df = search_companies(
        query=query,
        score_min=score_range[0],
        score_max=score_range[1],
        source="" if source == "Tümü" else source,
        limit=limit,
    )
    if df is None or df.empty:
        st.info("Veri gelince firma listesi burada görünecek.")
        return

    st.success(f"{len(df)} firma bulundu")
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.caption(f"Ortalama kalite skoru: {df['data_quality_score'].mean():.1f}/100")
