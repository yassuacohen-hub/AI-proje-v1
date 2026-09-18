"""P7-33: Admin Sistem Performansi sekmesi.

Sistem performans metrikleri: query latency, cache hit ratio,
slow query tespiti, Prometheus metrikleri, OpenTelemetry trace linking.

Kurallar:
  - st.cache_data ttl=30
  - kpi_karti kullanımı
  - /api/performance ve /metrics endpoint lerini kullan
"""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "src"))

from scripts.dash04_api_client import get_api, APIError
from web_dashboard.charts import kpi_karti
from web_dashboard.tabs.admin_error_handling import AdminErrorHandler

# Admin Performance logger
_admin_perf_logger = AdminErrorHandler("admin_performance")


@st.cache_data(ttl=30)
def load_performance_data() -> dict[str, Any]:
    """/api/performance endpoint'inden veri yukle."""
    try:
        data = get_api("/api/performance")
        if isinstance(data, dict) and data:
            return data
    except (APIError, Exception) as exc:
        _admin_perf_logger.warning("Performans verisi yüklenemedi", exc)
    return {}


@st.cache_data(ttl=30)
def load_ai_cost_per_call() -> dict[str, Any]:
    """P7-27: 9Router optimizer JSON'undan ortalama maliyet/çağrı ve latency özeti."""
    import json

    result: dict[str, Any] = {
        "ort_maliyet_cagri_usd": 0.0,
        "toplam_cagri": 0,
        "ort_latency_ms": 0.0,
    }
    try:
        json_path = Path("data/router/optimizer_latest.json")
        if not json_path.exists():
            return result
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        combo = data.get("combo_istatistik", {})
        usage = combo.get("usageHistory", {})
        req_detail = combo.get("requestDetails", {})

        toplam_maliyet = float(usage.get("toplam_maliyet_usd", 0.0))
        provider_cagri = usage.get("provider_cagri_sayisi", {})
        toplam_cagri = sum(int(v or 0) for v in provider_cagri.values())

        result["toplam_cagri"] = toplam_cagri
        result["ort_maliyet_cagri_usd"] = (
            toplam_maliyet / toplam_cagri if toplam_cagri > 0 else 0.0
        )
        result["ort_latency_ms"] = float(req_detail.get("ortalama_latency_ms", 0.0) or 0.0)
    except Exception as exc:
        _admin_perf_logger.warning("AI maliyet/çağrı yüklenemedi", exc)
    return result


@st.cache_data(ttl=60)
def load_prometheus_metrics() -> dict[str, Any]:
    """Prometheus metriklerini oku (/metrics endpointinden)."""
    try:
        import urllib.request

        url = "http://localhost:8000/metrics"
        req = urllib.request.Request(url, timeout=5)
        raw = urllib.request.urlopen(req).read().decode("utf-8")
        metrics: dict[str, Any] = {}
        for line in raw.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) >= 2:
                metrics[parts[0]] = parts[1]
        return metrics
    except Exception as exc:
        _admin_perf_logger.warning("Prometheus metrikleri yüklenemedi", exc)
        return {}


def render_performance_tab() -> None:
    """Sistem performansi sekmesini gosterir."""
    st.subheader("⏱️ Sistem Performansı")

    perf = load_performance_data()
    prom = load_prometheus_metrics()

    if not perf and not prom:
        st.info("Performans verisi yüklenemedi.")
        return

    ai_cost = load_ai_cost_per_call()

    # --- P7-27: AI Maliyet / Çağrı (9Router) ---
    st.divider()
    st.subheader("💰 AI Maliyet / Çağrı (9Router)")

    ac1, ac2, ac3 = st.columns(3)
    with ac1:
        kpi_karti("Ortalama Maliyet/Çağrı", f"${ai_cost['ort_maliyet_cagri_usd']:.5f}", kategori="sistem")
    with ac2:
        kpi_karti("Toplam Çağrı (Combo)", f"{ai_cost['toplam_cagri']:,}", kategori="sistem")
    with ac3:
        kpi_karti("Ortalama Latency (Combo)", f"{ai_cost['ort_latency_ms']:.0f} ms", kategori="sistem")
    # --- Ana Metrik Kartları ---
    st.divider()
    st.subheader("Query Latency")

    if perf:
        db_time = perf.get("db_time_ms", 0)
        query_count = perf.get("query_count", 0)
        avg_latency = round(db_time / max(1, query_count), 2) if query_count else 0

        c1, c2, c3 = st.columns(3)
        with c1:
            kpi_karti("Toplam DB Süre", f"{db_time:.2f} ms", kategori="sistem")
        with c2:
            kpi_karti("Sorgu Sayısı", f"{query_count:,}", kategori="sistem")
        with c3:
            kpi_karti("Ortalama Latency", f"{avg_latency:.2f} ms/sorgu", kategori="sistem")
    # --- Cache Hit Ratio ---
    st.divider()
    st.subheader("Cache Hit Ratio")

    if perf:
        cache_hits = perf.get("cache_hits", 0)
        cache_misses = perf.get("cache_misses", 0)
        cache_hit_rate = perf.get("cache_hit_rate", 0)

        c1, c2, c3 = st.columns(3)
        with c1:
            kpi_karti("Cache Hits", f"{cache_hits:,}", kategori="sistem")
        with c2:
            kpi_karti("Cache Misses", f"{cache_misses:,}", kategori="sistem")
        with c3:
            kpi_karti("Cache Hit Rate", f"{cache_hit_rate:.2%}", kategori="sistem")
    # --- Slow Queries ---
    st.divider()
    st.subheader("Yavaş Sorgular (>100ms)")

    if perf:
        slow_queries = perf.get("slow_queries", [])
        if slow_queries:
            sq_df = pd.DataFrame(slow_queries)
            st.dataframe(sq_df, width="stretch", hide_index=True)
            st.caption(f"Toplam yavaş sorgu: {len(slow_queries)}")
        else:
            st.success("Yavaş sorgu tespit edilmedi.")

    # --- Prometheus Metrikleri ---
    st.divider()
    st.subheader("Prometheus Metrikleri")

    if prom:
        huginn_keys = {k: v for k, v in prom.items() if k.startswith("huginn_")}
        if huginn_keys:
            pm_df = pd.DataFrame(
                [{"Metrik": k, "Değer": v} for k, v in huginn_keys.items()]
            )
            st.dataframe(pm_df, width="stretch", hide_index=True)
        else:
            st.info("Huginn metrikleri bulunamadı.")

        duration_keys = {k: v for k, v in prom.items() if "duration" in k.lower()}
        if duration_keys:
            st.subheader("Duration Metrikleri")
            for k, v in duration_keys.items():
                kpi_karti(k, v, kategori="sistem")
    else:
        st.info("Prometheus metrikleri yüklenemedi.")

    # --- OpenTelemetry Trace Linking ---
    st.divider()
    st.subheader("OpenTelemetry Trace Linking")

    otel_available = False
    try:
        from opentelemetry import trace as otel_trace
        otel_available = otel_trace.get_tracer_provider() is not None
    except ImportError:
        pass

    if otel_available:
        st.success("✅ OpenTelemetry aktif — trace linking mevcut.")
    else:
        st.warning("⚠️ OpenTelemetry mevcut değil. `opentelemetry-api` paketi kurulmalı.")

    st.caption(
        "Trace ID: her sorgu için trace_context kullanarak bağlanabilir. "
        "Jaeger/Zipkin arka ucunda trace_id göre sorgulama yapabilirsiniz."
    )

    # --- Report Generation ---
    st.divider()
    st.subheader("📊 Rapor Oluştur")

    if st.button("🔄 Performans Raporunu Oluştur"):
        report_lines = [
            f"# Sistem Performans Raporu",
            f" Tarih: {datetime.now().isoformat()}",
            f"",
            f"## Query Latency",
            f"- Toplam DB Süre: {perf.get('db_time_ms', 'N/A')} ms",
            f"- Sorgu Sayısı: {perf.get('query_count', 'N/A')}",
            f"",
            f"## Cache",
            f"- Hits: {perf.get('cache_hits', 'N/A')}",
            f"- Misses: {perf.get('cache_misses', 'N/A')}",
            f"- Hit Rate: {perf.get('cache_hit_rate', 'N/A')}",
            f"",
            f"## Slow Queries: {len(perf.get('slow_queries', []))}",
            f"",
        ]
        if prom:
            report_lines.append("## Prometheus Metrics\n")
            for k, v in prom.items():
                report_lines.append(f"- {k}: {v}")
            report_lines.append("")

        report_text = "\n".join(report_lines)
        st.json(report_text)
        st.download_button(
            label="📥 Raporu İndir (JSON)",
            data=report_text,
            file_name=f"performance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
        )

    st.caption("Son güncelleme: " + datetime.now().strftime("%Y-%m-%d %H:%M"))
