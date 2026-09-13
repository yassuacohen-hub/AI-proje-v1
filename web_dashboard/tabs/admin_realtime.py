# -*- coding: utf-8 -*-
"""P7-45: Canli Veri Akisi (SSE) Admin Sekmesi.

SSE endpoint: http://localhost:8000/api/intelligence/dashboard/stream
Kullanim: streamlit run app.py -> Sistem sekmesi
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

_load_env()

SSE_URL = "http://localhost:8000/api/intelligence/dashboard/stream"
CACHE_TTL = 5


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
    """Canli veri akisi sekmesi."""
    st.subheader("Canli Veri Akisi")

    son_guncelleme = datetime.now().strftime("%H:%M:%S")
    col_time, col_refresh, col_info = st.columns([3, 1, 1])
    with col_time:
        st.caption(f"Son güncelleme: {son_guncelleme} · {CACHE_TTL}s aralıkla otomatik yenileniyor")
    with col_refresh:
        if st.button("🔄 Yenile", key="refresh_realtime"):
            st.cache_data.clear()
            st.rerun()
    with col_info:
        with st.expander("ℹ️ Bu sekme hakkında"):
            st.markdown("""
**Amaç:** Gerçek zamanlı KPI ve sinyal takibi.

**Veri Kaynağı:** `/api/intelligence/dashboard/stream` (SSE)

**Kural:**
- Veri 5 saniyede bir otomatik yenilenir
- SSE bağlantısı kesildiğinde son bilinen veri gösterilir
- Cache TTL: 5 saniye
            """)

    st.divider()

    with st.spinner("Canli veri yükleniyor..."):
        sse = load_sse_data()
        kpi = load_kpi_from_db()

    if sse:
        st.markdown("### 📊 Canli Metrikler")
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

        st.divider()
        if sse.get("generated_at"):
            st.caption(f"Veri zamanı: {sse['generated_at']}")

        st.markdown("### 📈 Son 24 Saat Trend")
        trend = sse.get("trend", {})
        if trend:
            import pandas as pd
            trend_df = pd.DataFrame(trend)
            if not trend_df.empty:
                st.line_chart(trend_df, use_container_width=True)
        else:
            st.info("📊 Trend verisi henüz mevcut değil.")
    else:
        st.warning("⚠️ Canli bağlantı kurulamadı. SSE endpoint kontrol edin.")
        db = load_kpi_from_db()
        if db.get("total"):
            st.metric("DB Toplam Firma", f"{db['total']:,}")