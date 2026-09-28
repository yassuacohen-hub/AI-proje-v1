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

from company_master import sunum
from company_master.ui import PageHeader, Section, SectionNav
from web_dashboard.tabs.admin_kpi import load_admin_kpi_summary
from web_dashboard.tabs.admin_search import get_source_names, search_companies

#: ADMIN-UI-10 — Bolumler tek yerde tanimlanir (anchor tutarliligi).
BOLUMLER: tuple[Section, ...] = (
    Section("Operasyon Bildirimleri", "Son 24 saatteki yeni firma ve sinyal hareketi.",
            ikon="🔔", kimlik="musteri-bildirimleri"),
    Section("Filtreler", "Arama metni, kimlik tamlığı aralığı, kaynak ve satır sayısı.",
            ikon="🔍", kimlik="musteri-filtreleri"),
    Section("Firma Listesi", "Filtreye uyan firmalar ve ortalama kimlik tamlığı.",
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

    # K3-10g: rehber anahtarı sayfa altında (`app.REHBER_KEY`); modül yalnız okur.
    rehber = bool(st.session_state.get("_hg_rehber", False))
    col_btn, col_zaman = st.columns([1, 4], vertical_alignment="center")
    with col_btn:
        yenile = st.button("🔄 Veriyi Yenile", key="musteriler_yenile",
                           type="primary", width="stretch",
                           help="Önbelleği temizler ve firma listesini yeniden sorgular.")
    with col_zaman:
        st.caption("Firma listesi ve kalite görünümü · Son güncelleme: "
                   + datetime.now().strftime("%H:%M"))

    if yenile:
        st.cache_data.clear()
        st.rerun()

    if rehber:
        st.info(
            "**Bu ekran ne işe yarar?** Veritabanındaki firma kayıtlarını arar, kalite "
            "skoruna göre süzer ve eksik bilgi taşıyan (telefon, e-posta, web sitesi olmayan) "
            "kayıtları öne çıkarır. Veri temizliği ve müşteri araştırması için başlangıç "
            "noktasıdır.\n\n"
            "**Nasıl kullanılır?** Arama kutusuna firma adı veya NACE kodu yazın; kalite "
            "eşiğini kaydırıcıdan seçin. Sonuç tablosunda sütun başlığına tıklayarak "
            "sıralama yapabilirsiniz.\n\n"
            "**Veriler nereden gelir?** `companies` tablosu "
            "(`admin_search.search_companies` sorgusu).\n\n"
            "**Dikkat:** Liste, seçtiğiniz satır sayısı kadar kayıt gösterir. Tüm sonuçları "
            "indirmek için **Yönetim › Veri Export** ekranını kullanın."
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
    tavan = sunum.tavan_getir()
    col_query, col_score = st.columns([3, 2])
    with col_query:
        query = st.text_input("🔍 Firma ara", placeholder="Unvan, VKN, telefon, e-posta veya NACE", key="musteriler-query")
    with col_score:
        # Kaydirici 0-100 degil 0-tavan: puan 0-10 olceginde ve 6.50 uzeri
        # hicbir firmanin ulasamadigi bolge (D-250/7).
        score_range = st.slider(
            f"Kimlik Tamlığı (tavan {tavan:.2f})", 0.0, float(tavan), (0.0, float(tavan)),
            step=0.1, help=sunum.tavan_metni(tavan), key="musteriler-score",
        )

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
    st.dataframe(df, width="stretch", hide_index=True)
    st.caption(
        "Ortalama kimlik tamlığı: "
        + sunum.puan_metni(df["identity_completeness"].mean(), tavan)
    )
