#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Streamlit Dashboard â€” Company Master gÃ¶rsel arayÃ¼zÃ¼.

GÃ¶sterge paneli:
  - KPI kartlarÄ± (toplam firma, kalite skoru, alan doluluk oranlarÄ±)
  - GÃ¶rev tahtasÄ± (task_board.json'dan otomatik)
  - Ajan aktivite logu (AGENT_SYNC.md / handoffs.json'dan)
  - Veri kalitesi trendi (basit bar chart)
  - ğŸ”” Bildirim merkezi (auto-refresh + webhook event log) [P7-19]
  - ğŸ›¡ï¸ Admin paneli (sistem durumu, API metrikleri, kaynak durumu) [P7-20]
  - ğŸ“ˆ Performans paneli (response time, throughput, cache stats) [P7-21]

Ã‡alÄ±ÅŸtÄ±rma:
    streamlit run app.py
"""
from __future__ import annotations

import json
import sys
import time as _time
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd
import streamlit as st
from sqlalchemy import text

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from company_master.db.connection import get_engine
from company_master.orchestrator import task_board as tb
from scripts.dash04_api_client import get_api, APIError
from web_dashboard.tabs.admin_panel import render_decision_tab
from web_dashboard.tabs.admin_extras import render_api_management, render_user_management

st.set_page_config(page_title="Company Master Dashboard", layout="wide", page_icon="ğŸ¢")

# --- Performance tracking ---
if 'perf_metrics' not in st.session_state:
    st.session_state['perf_metrics'] = {
        'response_time': 0, 'query_count': 0, 'cache_hits': 0,
        'page_load_start': None, 'queries': []
    }
st.session_state['perf_metrics']['page_load_start'] = _time.perf_counter()

# --- Notification center state ---
if 'notifications' not in st.session_state:
    st.session_state['notifications'] = []
if 'last_refresh' not in st.session_state:
    st.session_state['last_refresh'] = datetime.now()
if 'auto_refresh_enabled' not in st.session_state:
    st.session_state['auto_refresh_enabled'] = True

# --- YardÄ±mcÄ±lar ---

@st.cache_data(ttl=30)
def load_kpi() -> dict:
    try:
        api_data = get_api("/api/kpi")
        if isinstance(api_data, dict) and api_data:
            return api_data
    except APIError:
        pass

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
            "GÃ¶rev ID": t.get("task_id", ""),
            "BaÅŸlÄ±k": t.get("baslik", ""),
            "Sahip": t.get("sahip", ""),
            "Ã–ncelik": t.get("oncelik", ""),
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
            "GÃ¶rev": tid,
            "Tamamlanan": (h.get("tamamlandi") or "")[:80],
            "Sonraki": (h.get("sonraki_adim") or "")[:80],
            "Tarih": h.get("tarih", "")[:19],
        })
    return pd.DataFrame(rows)


WEBHOOK_EVENTS = ROOT / "data" / "orchestrator" / "apify_webhook_events.jsonl"
WEBHOOK_DLQ = ROOT / "data" / "orchestrator" / "apify_webhook_dlq.jsonl"


@st.cache_data(ttl=10)
def load_webhook_stats() -> dict:
    """P7-19/20: Webhook olay ve hata sayaclarini jsonl dosyalarindan okur."""
    stats = {
        "olay_toplam": 0,
        "basarili": 0,
        "hatali": 0,
        "calisan": 0,
        "son_olay": None,
        "dlq_toplam": 0,
        "hata_turleri": {},
    }
    if WEBHOOK_EVENTS.exists():
        for line in WEBHOOK_EVENTS.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue
            stats["olay_toplam"] += 1
            status = (ev.get("status") or "").upper()
            if status == "SUCCEEDED":
                stats["basarili"] += 1
            elif status in ("FAILED", "ABORTED", "TIMED_OUT"):
                stats["hatali"] += 1
            else:
                stats["calisan"] += 1
            stats["son_olay"] = ev.get("triggered_at") or ev.get("timestamp") or stats["son_olay"]
    if WEBHOOK_DLQ.exists():
        lines = [ln for ln in WEBHOOK_DLQ.read_text(encoding="utf-8").splitlines() if ln.strip()]
        stats["dlq_toplam"] = len(lines)
        for line in lines:
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue
            et = ev.get("error_type") or "bilinmeyen"
            stats["hata_turleri"][et] = stats["hata_turleri"].get(et, 0) + 1
    return stats


def parse_prometheus_bytes(raw: str) -> dict:
    """P7-20/21: Apify webhook Prometheus metriklerini sozluge cevirir."""
    result: dict = {}
    for line in raw.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "{" in line and "}" in line and line.endswith("}"):
            continue  # multi-line metric olmayan satirlar
        parts = line.split()
        if len(parts) == 2:
            key, val = parts[0], parts[1]
            if key.startswith("apify_webhook_"):
                result[key] = val
    return result


# --- ArayÃ¼z ---

# Sidebar - kaynak filtreleme ve arama
with st.sidebar:
    st.header("ğŸ”§ Filtreler")
    search_query = st.text_input("ğŸ” Firma Ara", placeholder="Firma adÄ±, telefon, e-posta...")
    score_min = st.slider("Min Kalite Skoru", 0, 100, 0)
    score_max = st.slider("Maks Kalite Skoru", 0, 100, 100)
    
    st.divider()
    st.subheader("ğŸ“Š Veri KaynaklarÄ±")
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
        st.warning(f"Kaynaklar yÃ¼klenemedi: {e}")
    
    st.divider()
    st.subheader("ğŸ“ˆ HÄ±zlÄ± Ä°statistik")
    if st.button("ğŸ”„ Yenile", type="primary", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

# Refresh button
col_refresh, col_title = st.columns([1, 5])
with col_refresh:
    if st.button("ğŸ”„ Yenile", type="primary"):
        st.cache_data.clear()
        st.rerun()
with col_title:
    st.title("ğŸ¢ Company Master Dashboard")
st.caption(f"Son gÃ¼ncelleme: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Port: 8501")

# KPI kartlarÄ±
kpi = load_kpi()
if kpi:
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Toplam Firma", f"{kpi.get('total', 0):,}")
    col2.metric("Kalite Skoru", f"{kpi.get('avg_score', 0):.1f}/100")
    col3.metric("VKN", f"{kpi.get('vkn_either', 0):,}")
    col4.metric("Web Sitesi", f"{kpi.get('web', 0):,}")
    col5.metric("NACE", f"{kpi.get('nace', 0):,}")
    
    # Ä°kinci satÄ±r
    col6, col7, col8, col9, col10 = st.columns(5)
    col6.metric("Telefon", f"{kpi.get('tel', 0):,}")
    col7.metric("E-posta", f"{kpi.get('email', 0):,}")
    col8.metric("Adres", f"{kpi.get('adres', 0):,}")
    col9.metric("Parsel", f"{kpi.get('parsel', 0):,}")
    col10.metric("tax_number", f"{kpi.get('tax', 0):,}")

    st.subheader("ğŸ“Š Alan Doluluk OranlarÄ±")
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
    st.subheader("ğŸ“¥ ASO Ingest Durumu")
    try:
        with engine.connect() as conn:
            aso_total = conn.execute(text("""
                SELECT COUNT(*) FROM source_records sr
                WHERE sr.source_id = (SELECT source_id FROM sources WHERE source_name = 'aso.org.tr' LIMIT 1)
            """)).scalar()
            st.info(f"ASO kayÄ±tlarÄ±: {aso_total} | Toplam firma: {total:,} | Kalite skoru: {kpi.get('avg_score', 0):.1f}/100")
    except Exception as e:
        st.warning(f"ASO durumu yÃ¼klenemedi: {e}")

# GÃ¶rev tahtasÄ±
st.subheader("ğŸ“‹ GÃ¶rev TahtasÄ±")
tasks_df = load_tasks()
if not tasks_df.empty:
    st.dataframe(tasks_df, use_container_width=True, hide_index=True)
else:
    st.info("GÃ¶rev bulunamadÄ±.")

# Ajan aktivite logu
st.subheader("ğŸ¤– Ajan Aktivite Logu")
handoffs_df = load_handoffs()
if not handoffs_df.empty:
    st.dataframe(handoffs_df, use_container_width=True, hide_index=True)
else:
    st.info("HenÃ¼z handoff kaydÄ± yok.")

# Dosya yollarÄ±
st.subheader("ğŸ“ Veri DosyalarÄ±")
st.markdown(f"""
- **Task board:** `{ROOT / 'data/orchestrator/task_board.json'}`
- **GÃ¶rev panosu:** `{ROOT / 'data/orchestrator/gorev_panosu.md'}`
- **AGENT_SYNC:** `{ROOT / 'AGENT_SYNC.md'}`
- **KPI raporu:** `{ROOT / 'data/kpi_raporu.md'}`
- **OSTÄ°M detay:** `{ROOT / 'data/ostim/firmalar_detayli.jsonl'}`
- **ASO verisi:** `{ROOT / 'data/aso/aso_full.jsonl'}`
""")

# Firma tablosu (sidebar filtreleri ile)
st.subheader("ğŸ¢ Firma Listesi")
@st.cache_data(ttl=30)
def load_companies(search="", min_score=0, max_score=100, limit=200):
    api_params = {
        "search": search,
        "min_score": min_score,
        "max_score": max_score,
        "limit": limit,
    }
    try:
        api_data = get_api("/api/companies", params=api_params)
        if isinstance(api_data, dict):
            rows = api_data.get("items", [])
        elif isinstance(api_data, list):
            rows = api_data
        else:
            rows = []

        fields = [
            "legal_name",
            "trade_name",
            "website_domain",
            "primary_phone",
            "primary_email",
            "tax_number",
            "vergi_no",
            "nace_code",
            "data_quality_score",
        ]
        api_rows = [
            {field: row.get(field) for field in fields}
            for row in rows
            if isinstance(row, dict)
        ]
        if api_rows:
            return api_rows
    except APIError:
        pass

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
    df.columns = ["Firma AdÄ±", "Ticaret AdÄ±", "Web", "Telefon", "E-posta", "VKN", "Vergi No", "NACE", "Skor"]
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.caption(f"Toplam {len(companies)} firma gÃ¶steriliyor (skor {score_min}-{score_max})")
else:
    st.info("Filtrelerle eÅŸleÅŸen firma bulunamadÄ±.")

# --- P7-19: SSE GerÃ§ek ZamanlÄ± Bildirimler ---
webhook_stats = {}
try:
    webhook_stats = load_webhook_stats()
except Exception as e:
    st.warning(f"Webhook istatistikleri yuklenemedi: {e}")
st.subheader("ğŸ”” GerÃ§ek ZamanlÄ± Bildirimler")
if webhook_stats:
    notif_col1, notif_col2, notif_col3, notif_col4 = st.columns(4)
    with notif_col1:
        st.metric("âœ… BaÅŸarÄ±lÄ± Olay", webhook_stats["basarili"])
    with notif_col2:
        st.metric("âŒ HatalÄ± Olay", webhook_stats["hatali"])
    with notif_col3:
        st.metric("â³ Ã‡alÄ±ÅŸan", webhook_stats["calisan"])
    with notif_col4:
        st.metric("ğŸ“¦ DLQ (Hata KuyruÄŸu)", webhook_stats["dlq_toplam"])
    if webhook_stats["son_olay"]:
        st.caption(f"Son olay: {webhook_stats['son_olay']}")
    if webhook_stats["hatali"] > 0 or webhook_stats["dlq_toplam"] > 0:
        st.warning(f"âš ï¸ {webhook_stats['hatali']} hatalÄ± olay + {webhook_stats['dlq_toplam']} DLQ kaydÄ± incelemeyi bekliyor")
    else:
        st.success("âœ… Sistem saÄŸlÄ±klÄ± â€” yeni bildirim yok")
else:
    st.info("Bildirim verisi bulunamadÄ±")

# --- P7-20: Admin Panel ---
st.subheader("âš™ï¸ Admin Panel")
admin_tab1, admin_tab2, admin_tab3, admin_tab4, admin_tab5 = st.tabs(["📊 Sistem Durumu", "🔑 API Yönetimi", "📋 Webhook Metrikleri", "📋 Karar Defteri", "👥 Kullanıcı Yönetimi"])
if kpi is None or not kpi:
    kpi = load_kpi()
with admin_tab1:
    sys_col1, sys_col2, sys_col3, sys_col4 = st.columns(4)
    with sys_col1:
        st.metric("Toplam Firma", f"{kpi.get('total', 0):,}" if kpi else "â€”")
    with sys_col2:
        st.metric("Ort. Kalite", f"{kpi.get('avg_score', 0):.1f}" if kpi else "â€”")
    with sys_col3:
        st.metric("VKN Doluluk", f"%{kpi.get('vkn_either', 0) / max(kpi.get('total', 1), 1) * 100:.0f}" if kpi else "â€”")
    with sys_col4:
        dlq_ok = (webhook_stats.get("dlq_toplam", 0) == 0) if webhook_stats else True
        st.metric("Sistem Durumu", "ğŸŸ¢ SaÄŸlÄ±klÄ±" if dlq_ok else "ğŸŸ  Dikkat")
with admin_tab2:
    render_api_management()
with admin_tab3:
    if webhook_stats:
        hata_df = pd.DataFrame(
            [{"Hata TÃ¼rÃ¼": k, "Adet": v} for k, v in webhook_stats["hata_turleri"].items()]
        ) if webhook_stats["hata_turleri"] else pd.DataFrame(columns=["Hata TÃ¼rÃ¼", "Adet"])
        if not hata_df.empty:
            st.bar_chart(hata_df.set_index("Hata TÃ¼rÃ¼"), use_container_width=True)
        else:
            st.info("Webhook metrikleri: hata kaydÄ± yok â€” sistem temiz")
        met_col1, met_col2 = st.columns(2)
        with met_col1:
            st.metric("Toplam Webhook OlayÄ±", webhook_stats["olay_toplam"])
        with met_col2:
            st.metric("Hata OranÄ±", f"%{webhook_stats['hatali'] / max(webhook_stats['olay_toplam'], 1) * 100:.1f}")
    else:
        st.info("Webhook metrikleri yakÄ±nda aktif olacak")

with admin_tab4:
    render_decision_tab()

with admin_tab5:
    render_user_management()
# --- P7-21: Performans Metrikleri ---
st.subheader("â±ï¸ Performans Metrikleri")
if st.session_state['perf_metrics'].get('page_load_start'):
    load_ms = (_time.perf_counter() - st.session_state['perf_metrics']['page_load_start']) * 1000
    perf_col1, perf_col2, perf_col3, perf_col4 = st.columns(4)
    with perf_col1:
        st.metric("Sayfa YÃ¼kleme", f"{load_ms:.0f} ms")
    with perf_col2:
        st.metric("Webhook Olay", webhook_stats.get("olay_toplam", 0))
    with perf_col3:
        try:
            _toplam = webhook_stats.get("olay_toplam", 0)
            dlq_oran = webhook_stats.get("dlq_toplam", 0) / max(_toplam, 1) * 100
            st.metric("DLQ Hata OranÄ±", f"%{dlq_oran:.1f}")
        except Exception:
            st.metric("DLQ Hata OranÄ±", "%0")
    with perf_col4:
        st.metric("Cache TTL", "30 sn")
    try:
        trend_df = pd.DataFrame({
            "kaynak": ["Olay", "BaÅŸarÄ±lÄ±", "HatalÄ±", "DLQ"],
            "adet": [
                webhook_stats.get("olay_toplam", 0), webhook_stats.get("basarili", 0),
                webhook_stats.get("hatali", 0), webhook_stats.get("dlq_toplam", 0),
            ],
        })
        if trend_df["adet"].sum() > 0:
            st.caption("Webhook akÄ±ÅŸ daÄŸÄ±lÄ±mÄ±")
            st.bar_chart(trend_df.set_index("kaynak"), use_container_width=True)
    except Exception as e:
        st.info(f"Grafik oluÅŸturulamadÄ±: {e}")
    if st.button("ğŸ”„ Performans SayacÄ±nÄ± SÄ±fÄ±rla"):
        st.session_state['perf_metrics'] = {'response_time': 0, 'query_count': 0, 'cache_hits': 0, 'page_load_start': _time.perf_counter()}
        st.cache_data.clear()
        st.rerun()
else:
    st.info("Performans metrikleri burada gÃ¶rÃ¼necek")

