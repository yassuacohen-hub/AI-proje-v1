# -*- coding: utf-8 -*-
"""P7-45: Canli Veri Akisi (SSE) Admin Sekmesi.

SSE endpoint: http://localhost:8000/api/intelligence/dashboard/stream
Kullanim: streamlit run app.py -> Sistem sekmesi

ADMIN-UI-10:
  Sayfa iskeleti Playground dokumantasyon mantigina tasindi:
  ``PageHeader`` -> ``SectionNav`` -> ``Section``. Renk, ikon ve tipografi
  secimleri **degismedi**; yalnizca hiyerarsi disipline edildi. Ekranin tek
  birincil butonu "Veriyi Yenile" dugmesidir.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import requests
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "src"))

from company_master.db.connection import get_engine
from company_master.db.connection import _load_env
from company_master.ui import PageHeader, Section, SectionNav

_load_env()

SSE_URL = "http://localhost:8000/api/intelligence/dashboard/stream"
CACHE_TTL = 5

#: ADMIN-UI-10 — Bolumler tek yerde tanimlanir (anchor tutarliligi).
BOLUMLER: tuple[Section, ...] = (
    Section(
        "Canlı Metrikler",
        "Firma, sinyal, API çağrısı ve sistem sağlığı anlık değerleri.",
        ikon="📊",
        kimlik="canli-metrikler",
    ),
    Section(
        "Son 24 Saat Trend",
        "Aynı metriklerin zaman içindeki seyri.",
        ikon="📈",
        kimlik="trend-24s",
    ),
)

GIRIS_METNI = (
    "Gerçek zamanlı KPI ve sinyal akışını izleyin. Veri "
    f"{CACHE_TTL} saniyede bir otomatik yenilenir; SSE bağlantısı kesilirse "
    "son bilinen değerler gösterilir."
)


def _bolum(kimlik: str) -> Section:
    """Kimlige gore bolum tanimini getirir (anchor tutarliligi icin)."""
    for bolum in BOLUMLER:
        if bolum.kimlik == kimlik:
            return bolum
    raise KeyError(f"Tanımsız bölüm kimliği: {kimlik}")


@st.cache_data(ttl=CACHE_TTL)
def load_sse_data() -> dict[str, Any]:
    """SSE endpoint'den canli veri al."""
    try:
        resp = requests.get(SSE_URL, timeout=10)
        resp.raise_for_status()
        for line in resp.text.splitlines():
            line = line.strip()
            if line.startswith("data:"):
                data = json.loads(line[5:].strip())
                return data
    except Exception:
        pass
    return {}


@st.cache_data(ttl=CACHE_TTL)
def load_kpi_from_db() -> dict[str, Any]:
    """DB'den KPI al."""
    engine = get_engine()
    result: dict[str, Any] = {"total": 0, "signals": 0, "api_calls": 0}
    try:
        with engine.connect() as conn:
            row = conn.execute("SELECT COUNT(*) as cnt FROM companies").mappings().first()
            if row:
                result["total"] = row["cnt"] or 0
    except Exception:
        pass
    return result


def render_admin_realtime_tab() -> None:
    """Canli veri akisi sekmesi (ADMIN-UI-10 sayfa iskeletiyle)."""
    PageHeader(
        "Canlı Veri Akışı",
        giris=GIRIS_METNI,
        ust_etiket="Sistem · Canlı",
        ikon="📡",
    ).render()

    son_guncelleme = datetime.now().strftime("%H:%M:%S")
    col_btn, col_rehber, col_zaman = st.columns([1, 1, 3], vertical_alignment="center")
    with col_btn:
        yenile = st.button(
            "🔄 Veriyi Yenile",
            key="refresh_realtime",
            type="primary",
            width="stretch",
            help="Önbelleği temizler ve canlı akışı yeniden okur.",
        )
    with col_rehber:
        rehber = st.toggle(
            "ℹ️ Sekme rehberi",
            key="realtime_rehber",
            help="Bu ekranın amacını, veri kaynağını ve kısıtlarını gösterir.",
        )
    with col_zaman:
        st.caption(
            f"Son güncelleme: {son_guncelleme} · {CACHE_TTL}s aralıkla otomatik yenileniyor"
        )

    if yenile:
        st.cache_data.clear()
        st.rerun()

    if rehber:
        st.info(
            "**Amaç:** Gerçek zamanlı KPI ve sinyal takibi.\n\n"
            "**Veri kaynağı:** `/api/intelligence/dashboard/stream` (SSE).\n\n"
            f"**Kısıt:** Veri {CACHE_TTL} saniyede bir yenilenir; SSE bağlantısı "
            "kesildiğinde son bilinen veri gösterilir ve DB'den yedek okuma yapılır."
        )

    SectionNav(BOLUMLER, yatay=True).render()

    with st.spinner("Canli veri yükleniyor..."):
        sse = load_sse_data()
        kpi = load_kpi_from_db()

    if sse:
        _bolum("canli-metrikler").render()
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            total = sse.get("total", sse.get("total_firma", 0))
            st.metric("Toplam Firma", f"{total:,}".replace(",", ".") if total else "—")
            st.caption("📊 Artı mı azaldı mı?")
        with col2:
            signals = sse.get("signals", sse.get("sinyal_toplam", 0))
            st.metric("Sinyal", f"{signals:,}".replace(",", ".") if signals else "—")
            st.caption("📊 Spike var mı?")
        with col3:
            api = sse.get("api_calls", sse.get("api_cagri_toplam", 0))
            st.metric("API Çağrı", f"{api:,}".replace(",", ".") if api else "—")
            st.caption("📊 Artış trendi?")
        with col4:
            score = sse.get("quality_score", sse.get("saglik_skoru", 100))
            status = "🟢 Sağlıklı" if score and score >= 90 else "🟠 Dikkat"
            st.metric("Sistem Sağlığı", status, help=f"Skor: {score}")
            st.caption("📊 Kritik uyarı var mı?")

        if sse.get("generated_at"):
            st.caption(f"Veri zamanı: {sse['generated_at']}")

        _bolum("trend-24s").render()
        trend = sse.get("trend", {})
        if trend:
            import pandas as pd
            trend_df = pd.DataFrame(trend)
            if not trend_df.empty:
                st.line_chart(trend_df, width="stretch")
        else:
            st.info("📊 Trend verisi henüz mevcut değil.")
    else:
        st.warning("⚠️ Canli bağlantı kurulamadı. SSE endpoint kontrol edin.")
        db = load_kpi_from_db()
        if db.get("total"):
            st.metric("DB Toplam Firma", f"{db['total']:,}")