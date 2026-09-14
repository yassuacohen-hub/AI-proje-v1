# -*- coding: utf-8 -*-
"""Birlesik Sistem sekmesi.

Maliyet, performans, API analitigi, DLQ ve webhook izlemeyi tek operasyonel
sistem gorunumunde toplar. Veri yukleme ve alt sekme davranislari mevcut
modullerde tutulur.

ADMIN-UI-10:
  Sayfa iskeleti Playground dokumantasyon mantigina tasindi:
  ``PageHeader`` (ust etiket -> H1 -> giris) -> ``SectionNav`` -> ``Section``.
  Renk paleti, ikon seti ve tipografi secimleri **degismedi**; yalnizca
  hiyerarsi disipline edildi. Ekranin tek birincil butonu "Sistem Verilerini
  Yenile" dugmesidir.
"""
from __future__ import annotations

from datetime import datetime

import streamlit as st

from company_master.ui import PageHeader, Section, SectionNav
from web_dashboard.tabs.admin_api_analytics import render_api_analytics_tab
from web_dashboard.tabs.admin_cost import render_cost_tab
from web_dashboard.tabs.admin_dlq import render_dlq_tab
from web_dashboard.tabs.admin_performance import render_performance_tab
from web_dashboard.tabs.webhook_monitor import render_webhook_monitor_tab

#: ADMIN-UI-10 — Bolumler tek yerde tanimlanir; hem `SectionNav` hem de govde
#: ayni listeyi kullanir, boylece anchor'lar asla kaymaz.
BOLUMLER: tuple[Section, ...] = (
    Section(
        "Webhook ve DLQ",
        "Olay akisi ve islenemeyen kayit kuyrugu.",
        ikon="🔌",
        kimlik="webhook-dlq",
    ),
    Section(
        "Performans ve Maliyet",
        "Sorgu gecikmesi, kaynak kullanimi ve AI maliyeti.",
        ikon="⚡",
        kimlik="performans-maliyet",
    ),
    Section(
        "API Analitiği",
        "Uç nokta kullanımı ve tüketim dağılımı.",
        ikon="📊",
        kimlik="api-analitigi",
    ),
)

GIRIS_METNI = (
    "Maliyet, performans, API kullanımı, DLQ ve webhook sağlığını tek "
    "operasyonel görünümde izleyin. Boş paneller, ilgili veri kaynağı ilk "
    "veriyi ürettiğinde otomatik dolar."
)


def _bolum(kimlik: str) -> Section:
    """Kimlige gore bolum tanimini getirir (anchor tutarliligi icin)."""
    for bolum in BOLUMLER:
        if bolum.kimlik == kimlik:
            return bolum
    raise KeyError(f"Tanımsız bölüm kimliği: {kimlik}")


def render_sistem_tab() -> None:
    """Tum sistem operasyon panellerini tek sekmede render eder."""
    # --- ADMIN-UI-10: Playground kalibi — ust etiket -> H1 -> giris ---
    PageHeader(
        "Sistem",
        giris=GIRIS_METNI,
        ust_etiket="Sistem · Operasyon",
        ikon="⚙️",
    ).render()

    # --- Aksiyon seridi (tek birincil buton) ---
    col_refresh, col_time = st.columns([1, 3], vertical_alignment="center")
    with col_refresh:
        yenile = st.button(
            "🔄 Sistem Verilerini Yenile",
            key="sistem-refresh",
            type="primary",
            use_container_width=True,
            help="Önbelleği temizler ve tüm sistem panellerini yeniden yükler.",
        )
    with col_time:
        st.caption(f"Son güncelleme: {datetime.now().strftime('%H:%M')}")

    if yenile:
        st.cache_data.clear()
        st.rerun()

    # --- "Bu sayfada" gezinmesi (uzun ekrani taranabilir yapar) ---
    SectionNav(BOLUMLER, yatay=True).render()

    _bolum("webhook-dlq").render()
    render_webhook_monitor_tab()
    render_dlq_tab()

    _bolum("performans-maliyet").render()
    render_performance_tab()
    render_cost_tab()

    _bolum("api-analitigi").render()
    render_api_analytics_tab()
