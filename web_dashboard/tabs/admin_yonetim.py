# -*- coding: utf-8 -*-
"""Birlesik Yonetim sekmesi.

API/kullanici yonetimi, export, global arama ve otomatik yenileme panellerini
tek operasyonel yonetim gorunumunde toplar. Alt moduller kendi veri akislarini
ve aksiyonlarini korur.

ADMIN-UI-10:
  Sayfa iskeleti Playground dokumantasyon mantigina tasindi:
  ``PageHeader`` -> ``SectionNav`` -> ``Section``. Ikon, `SECTIONS` kaydiyla
  hizalandi (👨‍💼). Ekranin tek birincil butonu "Yönetim Verilerini Yenile".
"""
from __future__ import annotations

from datetime import datetime

import streamlit as st

from company_master.ui import PageHeader, Section, SectionNav
from web_dashboard.tabs.admin_auto_refresh import render_auto_refresh
from web_dashboard.tabs.admin_extras import render_api_management, render_user_management
from web_dashboard.tabs.admin_export import render_export_tab
from web_dashboard.tabs.admin_search import render_search_tab

#: ADMIN-UI-10 — Bolumler tek yerde tanimlanir (anchor tutarliligi).
BOLUMLER: tuple[Section, ...] = (
    Section(
        "API ve Kullanıcı Yönetimi",
        "Anahtar üretimi, yetki ve hesap işlemleri; admin girişi gerektirir.",
        ikon="🔑",
        kimlik="api-kullanici",
    ),
    Section(
        "Veri Araçları",
        "Global arama ve dışa aktarma işlemleri.",
        ikon="🧰",
        kimlik="veri-araclari",
    ),
    Section(
        "Otomatik Yenileme",
        "Panel yenileme aralığı ve zamanlayıcı durumu.",
        ikon="🔁",
        kimlik="otomatik-yenileme",
    ),
)

GIRIS_METNI = (
    "API, kullanıcı, dışa aktarma, arama ve yenileme ayarlarını tek yerden "
    "yönetin. Yetki gerektiren işlemler için admin girişi gereklidir."
)


def _bolum(kimlik: str) -> Section:
    """Kimlige gore bolum tanimini getirir (anchor tutarliligi icin)."""
    for bolum in BOLUMLER:
        if bolum.kimlik == kimlik:
            return bolum
    raise KeyError(f"Tanımsız bölüm kimliği: {kimlik}")


def render_yonetim_tab() -> None:
    """Yonetim panellerini tek sekmede render eder."""
    PageHeader(
        "Yönetim",
        giris=GIRIS_METNI,
        ust_etiket="Sistem · Yönetim",
        ikon="👨‍💼",
    ).render()

    col_refresh, col_time = st.columns([1, 3], vertical_alignment="center")
    with col_refresh:
        yenile = st.button(
            "🔄 Yönetim Verilerini Yenile",
            key="yonetim-refresh",
            type="primary",
            width="stretch",
            help="Önbelleği temizler ve yönetim panellerini yeniden yükler.",
        )
    with col_time:
        st.caption(f"Son güncelleme: {datetime.now().strftime('%H:%M')}")

    if yenile:
        st.cache_data.clear()
        st.rerun()

    SectionNav(BOLUMLER, yatay=True).render()

    _bolum("api-kullanici").render()
    render_api_management(token=st.session_state.get("admin_token"))
    render_user_management(token=st.session_state.get("admin_token"))

    _bolum("veri-araclari").render()
    render_search_tab()
    render_export_tab()

    _bolum("otomatik-yenileme").render()
    render_auto_refresh()
