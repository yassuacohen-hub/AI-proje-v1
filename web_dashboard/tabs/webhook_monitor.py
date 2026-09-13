"""P7-26: Webhook Monitor Sekmesi — endpoint, latency, status dagilimi, hata loglari.

Kurallar:
  - st.cache_data ttl=10
  - JSONL dosyalarindan okuma (events + DLQ)
  - ApifyWebhookReceiver.health_check() ile endpoint durumu
  - Plotly fallback: st.bar_chart / st.pyplot
  - Hata yuzeyinde graceful fallback (dosya yok -> "veri yok")
"""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "src"))

from scripts.apify_webhook_receiver import ApifyWebhookReceiver

WEBHOOK_EVENTS = ROOT / "data" / "orchestrator" / "apify_webhook_events.jsonl"
WEBHOOK_DLQ = ROOT / "data" / "orchestrator" / "apify_webhook_dlq.jsonl"


# ---------------------------------------------------------------------------
# Veri Yükleme Fonksiyonları
# ---------------------------------------------------------------------------

@st.cache_data(ttl=10)
def load_webhook_stats() -> dict[str, Any]:
    """Webhook olay ve hata sayacilarini jsonl dosyalarindan okur."""
    stats: dict[str, Any] = {
        "olay_toplam": 0,
        "basarili": 0,
        "hatali": 0,
        "calisan": 0,
        "son_olay": None,
        "dlq_toplam": 0,
        "hata_turleri": {},
        "olaylar": [],
        "dlq_girdileri": [],
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
            stats["olaylar"].append(ev)
    if WEBHOOK_DLQ.exists():
        for line in WEBHOOK_DLQ.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                ev = json.loads(line)
            except json.JSONDecodeError:
                continue
            stats["dlq_toplam"] += 1
            et = ev.get("error_type") or "bilinmeyen"
            stats["hata_turleri"][et] = stats["hata_turleri"].get(et, 0) + 1
            stats["dlq_girdileri"].append(ev)
    return stats


@st.cache_data(ttl=60)
def load_health_check() -> dict[str, Any]:
    """Apify webhook alicinin health check durumu."""
    try:
        receiver = ApifyWebhookReceiver()
        return receiver.health_check()
    except Exception:
        return {}


@st.cache_data(ttl=60)
def load_prometheus_metrics() -> dict[str, Any]:
    """Prometheus metriklerini oku (web_app.py API üzerinden)."""
    try:
        import urllib.request

        url = "http://localhost:8000/api/webhooks/apify/metrics"
        req = urllib.request.Request(url, timeout=5)
        raw = urllib.request.urlopen(req).read().decode("utf-8")
        metrics: dict[str, Any] = {}
        for line in raw.splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) >= 2 and parts[0].startswith("apify_webhook_"):
                metrics[parts[0]] = parts[1]
        return metrics
    except Exception:
        return {}


# ---------------------------------------------------------------------------
# Yardımcı Fonksiyonlar
# ---------------------------------------------------------------------------

def _status_color(status: str) -> str:
    if status in ("SUCCEEDED", "ok"):
        return "🟢"
    if status in ("FAILED", "rejected"):
        return "🔴"
    if status == "ABORTED":
        return "🟠"
    if status == "TIMED_OUT":
        return "🟡"
    return "⚪"


def _format_ts(ts: Any) -> str:
    if ts is None:
        return "—"
    try:
        if isinstance(ts, str):
            return ts[:19]
        return str(ts)[:19]
    except Exception:
        return str(ts)


# ---------------------------------------------------------------------------
# Render Fonksiyonu
# ---------------------------------------------------------------------------

def render_webhook_monitor_tab() -> None:
    """P7-26: Webhook Monitor sekmesi."""

    st.subheader("🔌 Webhook Monitor")
    st.caption(
        "Apify ingest pipeline health, DLQ, rate limit, latency ve hata loglari — "
        "son güncelleme: " + datetime.now().strftime("%Y-%m-%d %H:%M")
    )

    # --- Health Check ---
    st.divider()
    st.subheader("🏥 Endpoint Durumu")

    health = load_health_check()
    if health:
        h1, h2, h3, h4, h5, h6 = st.columns(6)
        status_val = health.get("status", "unknown")
        dlq_size = health.get("dlq_size", 0)
        with h1:
            st.metric(
                "Durum",
                status_val.upper(),
                delta=None,
            )
        with h2:
            st.metric(
                "Secret",
                "✅ Var" if health.get("secret_configured") else "❌ Yok",
            )
        with h3:
            st.metric(
                "Rate Limit",
                "Aktif" if health.get("rate_limit_enabled") else "Devre Dışı",
            )
        with h4:
            st.metric("DLQ Boyutu", dlq_size)
        with h5:
            st.metric(
                "Cache",
                f"{health.get('processed_runs_memory', 0)} çalışma",
            )
        with h6:
            prom = health.get("prometheus_available", False)
            st.metric("Prometheus", "✅" if prom else "❌")

        if status_val == "healthy":
            st.success("✅ Webhook alıcısı sağlıklı.")
        elif status_val == "degraded":
            st.warning("🟠 Webhook alıcısı degrade durumda — inceleme gerekiyor.")
        else:
            st.error(f"🔴 Webhook alıcısı: {status_val}")
    else:
        st.info("Health check verisi yüklenemedi.")

    # --- Istatistik Kartları ---
    st.divider()
    st.subheader("📊 Webhook Olay İstatistikleri")

    stats = load_webhook_stats()

    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.metric("Toplam Olay", stats["olay_toplam"])
    with c2:
        st.metric("✅ Başarılı", stats["basarili"])
    with c3:
        st.metric("❌ Hatalı", stats["hatali"])
    with c4:
        st.metric("⏳ Çalışan", stats["calisan"])
    with c5:
        st.metric("📦 DLQ", stats["dlq_toplam"])

    if stats["son_olay"]:
        st.caption(f"Son olay: {stats['son_olay']}")

    # --- Status Dagilimi ---
    st.divider()
    st.subheader("📈 Durum Dağılımı")

    if stats["olay_toplam"] > 0:
        status_counts: dict[str, int] = {"SUCCEEDED": 0, "FAILED": 0, "ABORTED": 0, "TIMED_OUT": 0, "other": 0}
        for ev in stats["olaylar"]:
            status = (ev.get("status") or "").upper()
            if status in status_counts:
                status_counts[status] += 1
            else:
                status_counts["other"] += 1

        status_df = pd.DataFrame(
            [
                {"Durum": "SUCCEEDED", "Adet": status_counts["SUCCEEDED"]},
                {"Durum": "FAILED", "Adet": status_counts["FAILED"]},
                {"Durum": "ABORTED", "Adet": status_counts["ABORTED"]},
                {"Durum": "TIMED_OUT", "Adet": status_counts["TIMED_OUT"]},
                {"Durum": "Diğer", "Adet": status_counts["other"]},
            ]
        )
        status_df = status_df[status_df["Adet"] > 0]

        d1, d2 = st.columns([1, 2])
        with d1:
            st.bar_chart(status_df.set_index("Durum")["Adet"], use_container_width=True)
        with d2:
            try:
                import plotly.express as px

                fig = px.pie(
                    status_df,
                    values="Adet",
                    names="Durum",
                    title="Durum Dağılımı",
                    color="Durum",
                )
                fig.update_layout(height=300, margin=dict(t=40, b=20))
                st.plotly_chart(fig, use_container_width=True)
            except ImportError:
                st.bar_chart(status_df.set_index("Durum")["Adet"], use_container_width=True)
    else:
        st.info("Henüz webhook olay kaydı bulunmuyor.")

    # --- Hata Türleri ---
    if stats["hata_turleri"]:
        st.divider()
        st.subheader("🔍 Hata Türleri")
        err_df = pd.DataFrame(
            [{"Hata Türü": k, "Adet": v} for k, v in stats["hata_turleri"].items()]
        ).sort_values("Adet", ascending=False)
        st.bar_chart(err_df.set_index("Hata Türü")["Adet"], use_container_width=True)

    # --- DLQ Girdileri ---
    if stats["dlq_girdileri"]:
        st.divider()
        st.subheader("📦 Dead-Letter Queue (DLQ) Kayıtları")

        dlq_rows = []
        for entry in stats["dlq_girdileri"][-50:]:
            dlq_rows.append(
                {
                    "Hata Türü": entry.get("error_type", "bilinmeyen"),
                    "Zaman": _format_ts(
                        entry.get("timestamp") or entry.get("created_at") or entry.get("time")
                    ),
                    "Açıklama": str(entry.get("reason", entry.get("detail", "")))[:120],
                    "Payload": str(entry.get("raw_body", ""))[:80],
                }
            )
        dlq_df = pd.DataFrame(dlq_rows)
        if not dlq_df.empty:
            st.dataframe(dlq_df, use_container_width=True, hide_index=True)
            st.caption(
                f"Toplam {stats['dlq_toplam']} DLQ kaydı gösteriliyor (son 50)."
            )
    else:
        st.divider()
        st.subheader("📦 Dead-Letter Queue (DLQ)")
        st.info("DLQ boş — hatalı olay kaydı yok.")

    # --- Latency (Prometheus) ---
    st.divider()
    st.subheader("⏱️ Latency (Prometheus)")

    prom = load_prometheus_metrics()
    if prom:
        latency_keys = {
            k: v for k, v in prom.items() if "duration" in k.lower()
        }
        if latency_keys:
            for k, v in latency_keys.items():
                st.metric(k, v)
        else:
            st.info("Prometheus metrikleri mevcut ancak latency verisi yok.")
    else:
        st.info("Prometheus metrikleri yüklenemedi (API erişilebilir değil veya prometheus-client kurulu değil).")
