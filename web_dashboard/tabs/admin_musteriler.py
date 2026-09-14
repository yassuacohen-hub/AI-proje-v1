# -*- coding: utf-8 -*-
"""Musteriler ekrani: firma listesi, filtreler ve operasyon bildirimleri.

ADMIN-UI-10:
  Sayfa iskeleti Playground dokumantasyon mantigina tasindi:
  ``PageHeader`` -> ``SectionNav`` -> ``Section``. Renk, ikon ve tipografi
  secimleri **degismedi**; yalnizca hiyerarsi disipline edildi. Ekranin tek
  birincil butonu "Veriyi Yenile" dugmesidir.
"""
from __future__ import annotations

from datetime import datetime

import pandas as pd  # noqa: F401  (tablo tipleri icin dolayli bagimlilik)
import streamlit as st

from company_master.ui import PageHeader, Section, SectionNav
from web_dashboard.tabs.admin_kpi import load_admin_kpi_summary
from web_dashboard.tabs.admin_search import get_source_names, search_companies

#: ADMIN-UI-10 — Bolumler tek yerde tanimlanir (anchor tutarliligi).
BOLUMLER: tuple[Section, ...] = (
    Section("Operasyon Bildirimleri", "Son 24 saatteki yeni firma ve sinyal hareketi.",
            ikon="🔔", kimlik="musteri-bildirimleri"),
    Section("Filtreler", "Arama metni, kalite skoru aralığı, kaynak ve satır sayısı.",
            ikon="🔍", kimlik="musteri-filtreleri"),
    Section("Firma Listesi", "Filtreye uyan firmalar ve ortalama kalite skoru.",
            ikon="📋", kimlik="musteri-listesi"),
)

GIRIS_METNI = (
    "Firma kayıtlarını tek ekrandan arayın ve kalite skoruna göre süzün. "
    "Düşük skorlu kayıtlar genellikle eksik iletişim bilgisi veya doğrulanmamış "
    "VKN taşır; önce bunları inceleyin."
)


def _bolum(kimlik: str) -> Section:
    """Kimlige gore bolum tanimini getirir (anchor tutarliligi icin)."""
    for bolum in BOLUMLER:
        if bolum.kimlik == kimlik:
            return bolum
    raise KeyError(f"Tanımsız bölüm kimliği: {kimlik}")


def _render_baslik() -> None:
    """ADMIN-UI-10: Playground kalibi — ust etiket -> H1 -> giris -> aksiyonlar."""
    PageHeader("Müşteriler", giris=GIRIS_METNI,
               ust_etiket="İş · Müşteriler", ikon="👥").render()

    col_btn, col_rehber, col_zaman = st.columns([1, 1, 3], vertical_alignment="center")
    with col_btn:
        yenile = st.button("🔄 Veriyi Yenile", key="musteriler_yenile",
                           type="primary", use_container_width=True,
                           help="Önbelleği temizler ve firma listesini yeniden sorgular.")
    with col_rehber:
        rehber = st.toggle("ℹ️ Sekme rehberi", key="musteriler_rehber",
                           help="Bu ekranın amacını, veri kaynağını ve kısıtlarını gösterir.")
    with col_zaman:
        st.caption("Firma listesi ve kalite görünümü · Son güncelleme: "
                   + datetime.now().strftime("%H:%M"))

    if yenile:
        st.cache_data.clear()
        st.rerun()

    if rehber:
        st.info(
            "**Amaç:** Firma kayıtlarını aramak, kalite skoruna göre süzmek ve "
            "eksik veri taşıyan kayıtları öne çıkarmak.\n\n"
            "**Veri kaynağı:** `companies` tablosu (`admin_search.search_companies`).\n\n"
            "**Kısıt:** Liste en fazla seçilen satır sayısı kadar kayıt gösterir; "
            "tam dışa aktarım için rapor ekranını kullanın."
        )

    SectionNav(BOLUMLER, yatay=True).render()


def render_musteriler_tab() -> None:
    """Firma listesini filtreler ve kritik kalite bildirimlerini gosterir."""
    _render_baslik()

    _bolum("musteri-bildirimleri").render()
    kpi = load_admin_kpi_summary()
    if kpi:
        st.info(
            f"Bildirim: {kpi.get('son_24s_yeni_firma', 0)} yeni firma, "
            f"{kpi.get('sinyal_toplam', 0)} toplam sinyal. "
            "Kalitesi düşük firmaları filtreleyerek inceleyin."
        )
    else:
        st.info("Bildirim verisi henüz hazır değil; firma verisi geldiğinde burada görünecek.")

    _bolum("musteri-filtreleri").render()
    col_query, col_score = st.columns([3, 2])
    with col_query:
        query = st.text_input("🔍 Firma ara", placeholder="Unvan, VKN, telefon, e-posta veya NACE", key="musteriler-query")
    with col_score:
        score_range = st.slider("Kalite skoru", 0, 100, (0, 100), key="musteriler-score")

    sources = get_source_names()
    source = st.selectbox("Kaynak", ["Tümü"] + sources, key="musteriler-source")
    limit = st.selectbox("Gösterilecek firma", [50, 100, 200], key="musteriler-limit")

    _bolum("musteri-listesi").render()
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
