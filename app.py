#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Streamlit Dashboard — Company Master görsel arayüzü.

Gösterge paneli:
  - KPI kartları (toplam firma, kalite skoru, alan doluluk oranları)
  - Görev tahtası (task_board.json'dan otomatik)
  - Ajan aktivite logu (AGENT_SYNC.md / handoffs.json'dan)
  - Veri kalitesi trendi (basit bar chart)

Çalıştırma:
    streamlit run app.py
"""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st
from sqlalchemy import text

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from company_master.db.connection import get_engine
from company_master.orchestrator import task_board as tb

st.set_page_config(page_title="Company Master Dashboard", layout="wide")

# --- Performance tracking ---
if 'perf_metrics' not in st.session_state:
    st.session_state['perf_metrics'] = {'response_time': 0, 'query_count': 0, 'cache_hits': 0, 'page_load_start': None}

import time as _time
st.session_state['perf_metrics']['page_load_start'] = _time.perf_counter()

# --- Yardımcılar ---

@st.cache_data(ttl=30)
def load_kpi() -> dict:
    engine = get_engine()
    with engine.connect() as conn:
        r = conn.execute(text("""
            SELECT COUNT(*) as total,
                SUM(CASE WHEN c.tax_number IS NOT NULL AND c.tax_number != '' THEN 1 ELSE 0 END) as tax,
                SUM(CASE WHEN c.vergi_no IS NOT NULL AND c.vergi_no != '' THEN 1 ELSE 0 END) as vergi,
                SUM(CASE WHEN COALESCE(c.tax_number, c.vergi_no) IS NOT NULL AND COALESCE(c.tax_number, c.vergi_no) != '' THEN 1 ELSE 0 END) as vkn_either,
                SUM(CASE WHEN c.website_domain IS NOT NULL AND c.website_domain != '' THEN 1 ELSE 0 END) as web,
                SUM(CASE WHEN c.osb_parsel IS NOT NULL AND c.osb_parsel != '' THEN 1 ELSE 0 END) as parsel,
                SUM(CASE WHEN c.adres IS NOT NULL AND c.adres != '' THEN 1 ELSE 0 END) as adres,
                SUM(CASE WHEN c.primary_phone IS NOT NULL AND c.primary_phone != '' THEN 1 ELSE 0 END) as tel,
                SUM(CASE WHEN c.primary_email IS NOT NULL AND c.primary_email != '' THEN 1 ELSE 0 END) as email,
                SUM(CASE WHEN c.nace_code IS NOT NULL AND c.nace_code != '' THEN 1 ELSE 0 END) as nace,
                AVG(c.data_quality_score) as avg_score
            FROM companies c
            WHERE c.is_ankara=TRUE AND c.is_osb_member=TRUE
        """)).mappings().first()
        return dict(r) if r else {}


@st.cache_data(ttl=30)
def load_tasks() -> pd.DataFrame:
    board = tb.gorev_listesi()
    if not board:
        return pd.DataFrame()
    rows = []
    for t in board:
        rows.append({
            "Görev ID": t.get("task_id", ""),
            "Başlık": t.get("baslik", ""),
            "Sahip": t.get("sahip", ""),
            "Öncelik": t.get("oncelik", ""),
            "Durum": t.get("durum", ""),
            "Not": (t.get("not") or "")[:60],
        })
    return pd.DataFrame(rows)


@st.cache_data(ttl=30)
def load_handoffs() -> pd.DataFrame:
    handoffs = tb.handoff_tum()
    if not handoffs:
        return pd.DataFrame()
    rows = []
    for tid, h in handoffs.items():
        rows.append({
            "Görev": tid,
            "Tamamlanan": (h.get("tamamlandi") or "")[:80],
            "Sonraki": (h.get("sonraki_adim") or "")[:80],
            "Tarih": h.get("tarih", "")[:19],
        })
    return pd.DataFrame(rows)


# --- Arayüz ---

# Sidebar - kaynak filtreleme ve arama
with st.sidebar:
    st.header("🔧 Filtreler")
    search_query = st.text_input("🔍 Firma Ara", placeholder="Firma adı, telefon, e-posta...")
    score_min = st.slider("Min Kalite Skoru", 0, 100, 0)
    score_max = st.slider("Maks Kalite Skoru", 0, 100, 100)
    
    st.divider()
    st.subheader("📊 Veri Kaynakları")
    try:
        @st.cache_data(ttl=30)
        def _load_sources():
            engine = get_engine()
            with engine.connect() as conn:
                sources = conn.execute(text("""
                    SELECT s.source_name, COUNT(sr.source_record_id) as cnt
                FROM sources s
                LEFT JOIN source_records sr ON sr.source_id = s.source_id
                GROUP BY s.source_id, s.source_name
                ORDER BY cnt DESC
            """)).mappings().all()
            for s in sources:
                return sources
            return []
        sources = _load_sources()
        for s in sources:
            st.metric(s["source_name"], f"{s['cnt']:,}")
    except Exception as e:
        st.warning(f"Kaynaklar yüklenemedi: {e}")
    
    st.divider()
    st.subheader("📈 Hızlı İstatistik")
    if st.button("🔄 Yenile", type="primary", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# Refresh button
col_refresh, col_title = st.columns([1, 5])
with col_refresh:
    if st.button("🔄 Yenile", type="primary"):
        st.cache_data.clear()
        st.rerun()
with col_title:
    st.title("🏢 Company Master Dashboard")
st.caption(f"Son güncelleme: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Port: 8501")

# KPI kartları
kpi = load_kpi()
if kpi:
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Toplam Firma", f"{kpi.get('total', 0):,}")
    col2.metric("Kalite Skoru", f"{kpi.get('avg_score', 0):.1f}/100")
    col3.metric("VKN", f"{kpi.get('vkn_either', 0):,}")
    col4.metric("Web Sitesi", f"{kpi.get('web', 0):,}")
    col5.metric("NACE", f"{kpi.get('nace', 0):,}")
    
    # İkinci satır
    col6, col7, col8, col9, col10 = st.columns(5)
    col6.metric("Telefon", f"{kpi.get('tel', 0):,}")
    col7.metric("E-posta", f"{kpi.get('email', 0):,}")
    col8.metric("Adres", f"{kpi.get('adres', 0):,}")
    col9.metric("Parsel", f"{kpi.get('parsel', 0):,}")
    col10.metric("tax_number", f"{kpi.get('tax', 0):,}")

    st.subheader("📊 Alan Doluluk Oranları")
    fields = {
        "Telefon": kpi.get("tel", 0),
        "E-posta": kpi.get("email", 0),
        "Web": kpi.get("web", 0),
        "VKN": kpi.get("vkn_either", 0),
        "NACE": kpi.get("nace", 0),
        "Adres": kpi.get("adres", 0),
        "Parsel": kpi.get("parsel", 0),
    }
    total = max(kpi.get("total", 1), 1)
    chart_df = pd.DataFrame({
        "alan": list(fields.keys()),
        "dolu": list(fields.values()),
        "oran": [v / total * 100 for v in fields.values()],
    })
    st.bar_chart(chart_df.set_index("alan")["oran"], use_container_width=True)
    
    # ASO ingest durumu
    st.subheader("📥 ASO Ingest Durumu")
    try:
        with engine.connect() as conn:
            aso_total = conn.execute(text("""
                SELECT COUNT(*) FROM source_records sr
                WHERE sr.source_id = (SELECT source_id FROM sources WHERE source_name = 'aso.org.tr' LIMIT 1)
            """)).scalar()
            st.info(f"ASO kayıtları: {aso_total} | Toplam firma: {total:,} | Kalite skoru: {kpi.get('avg_score', 0):.1f}/100")
    except Exception as e:
        st.warning(f"ASO durumu yüklenemedi: {e}")

# Görev tahtası
st.subheader("📋 Görev Tahtası")
tasks_df = load_tasks()
if not tasks_df.empty:
    st.dataframe(tasks_df, use_container_width=True, hide_index=True)
else:
    st.info("Görev bulunamadı.")

# Ajan aktivite logu
st.subheader("🤖 Ajan Aktivite Logu")
handoffs_df = load_handoffs()
if not handoffs_df.empty:
    st.dataframe(handoffs_df, use_container_width=True, hide_index=True)
else:
    st.info("Henüz handoff kaydı yok.")

# Dosya yolları
st.subheader("📁 Veri Dosyaları")
st.markdown(f"""
- **Task board:** `{ROOT / 'data/orchestrator/task_board.json'}`
- **Görev panosu:** `{ROOT / 'data/orchestrator/gorev_panosu.md'}`
- **AGENT_SYNC:** `{ROOT / 'AGENT_SYNC.md'}`
- **KPI raporu:** `{ROOT / 'data/kpi_raporu.md'}`
- **OSTİM detay:** `{ROOT / 'data/ostim/firmalar_detayli.jsonl'}`
- **ASO verisi:** `{ROOT / 'data/aso/aso_full.jsonl'}`
""")

# Firma tablosu (sidebar filtreleri ile)
st.subheader("🏢 Firma Listesi")
@st.cache_data(ttl=30)
def load_companies(search="", min_score=0, max_score=100, limit=200):
    engine = get_engine()
    with engine.connect() as conn:
        params = {"min_score": min_score, "max_score": max_score, "limit": limit}
        where = "c.is_ankara=TRUE AND c.is_osb_member=TRUE AND c.data_quality_score >= :min_score AND c.data_quality_score <= :max_score"
        if search:
            where += " AND (LOWER(c.legal_name) LIKE :search OR LOWER(c.primary_phone) LIKE :search OR LOWER(c.primary_email) LIKE :search)"
            params["search"] = f"%{search.lower()}%"
        rows = conn.execute(text(f"""
            SELECT c.legal_name, c.trade_name, c.website_domain, c.primary_phone, c.primary_email,
                   c.tax_number, c.vergi_no, c.nace_code, c.data_quality_score
            FROM companies c
            WHERE {where}
            ORDER BY c.data_quality_score DESC
            LIMIT :limit
        """), params).mappings().all()
        return [dict(r) for r in rows]

companies = load_companies(search_query, score_min, score_max)
if companies:
    df = pd.DataFrame(companies)
    df.columns = ["Firma Adı", "Ticaret Adı", "Web", "Telefon", "E-posta", "VKN", "Vergi No", "NACE", "Skor"]
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.caption(f"Toplam {len(companies)} firma gösteriliyor (skor {score_min}-{score_max})")
else:
    st.info("Filtrelerle eşleşen firma bulunamadı.")

# --- Performance Report ---
st.subheader("⏱️ Dashboard Performans Raporu")
if st.session_state['perf_metrics'].get('page_load_start'):
    load_ms = (_time.perf_counter() - st.session_state['perf_metrics']['page_load_start']) * 1000
    st.metric("Sayfa Yükleme Süresi", f"{load_ms:.0f} ms")
    st.metric("API Sorgu Sayısı", st.session_state['perf_metrics'].get('query_count', 0))
    st.metric("Cache Hit", st.session_state['perf_metrics'].get('cache_hits', 0))
    if st.button("🔄 Performans Sayacını Sıfırla"):
        st.session_state['perf_metrics'] = {'response_time': 0, 'query_count': 0, 'cache_hits': 0, 'page_load_start': _time.perf_counter()}
        st.rerun()
