"""P7-38: Webhook DLQ Dashboard — Apify webhook hata kuyrugu izleme.

DLQ girdilerini goruntuler, hata istatistikleri, retry
istatistikleri ve filtreleme sunar.

Kurallar:
  - st.cache_data ttl=30
  - st.metric kullanımı
  - JSONL dosyalarindan okuma
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st
from web_dashboard.charts import kpi_karti

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "src"))

from scripts.apify_webhook_receiver import ApifyWebhookReceiver

DLQ_PATH = ROOT / "data" / "orchestrator" / "apify_webhook_dlq.jsonl"


@st.cache_data(ttl=30)
def load_dlq_stats() -> dict[str, Any]:
    """DLQ istatistiklerini jsonl dosyasindan okur."""
    stats: dict[str, Any] = {
        "dlq_toplam": 0,
        "hata_turleri": {},
        "ortalama_yas_saat": 0,
        "en_eski": None,
        "en_yeni": None,
        "retryable": 0,
        "non_retryable": 0,
        "entries": [],
    }
    if not DLQ_PATH.exists():
        return stats

    total_age = 0.0
    count_age = 0
    for line in DLQ_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            ev = json.loads(line)
        except json.JSONDecodeError:
            continue
        stats["dlq_toplam"] += 1
        et = ev.get("error_type", "unknown")
        stats["hata_turleri"][et] = stats["hata_turleri"].get(et, 0) + 1
        ts = ev.get("timestamp", "")
        try:
            dt = datetime.fromisoformat(ts)
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            age = (datetime.now(timezone.utc) - dt).total_seconds() / 3600
            total_age += age
            count_age += 1
            if stats["en_eski"] is None or dt < stats["en_eski"]:
                stats["en_eski"] = dt.isoformat()
            if stats["en_yeni"] is None or dt > stats["en_yeni"]:
                stats["en_yeni"] = dt.isoformat()
        except (ValueError, TypeError):
            pass
        error = ev.get("error", "").lower()
        if "auth" in error or "secret" in error or "rate" in error:
            stats["retryable"] += 1
        else:
            stats["non_retryable"] += 1
        stats["entries"].append(ev)

    if count_age > 0:
        stats["ortalama_yas_saat"] = round(total_age / count_age, 2)

    return stats


def render_dlq_tab() -> None:
    """DLQ dashboard sekmesini gosterir."""
    st.subheader("🔌 Webhook DLQ Dashboard")

    stats = load_dlq_stats()

    if stats["dlq_toplam"] == 0:
        st.success("DLQ boş — aktif hata kuyruğu yok.")
        return

    # --- Anlık Istatistikler ---
    st.divider()
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        kpi_karti("Toplam DLQ", f"{stats['dlq_toplam']:,}", kategori="uyari")
    with c2:
        retry = stats.get("retryable", 0)
        kpi_karti("Retry", f"{retry:,}", kategori="uyari")
    with c3:
        kpi_karti("Non-Retry", f"{stats.get('non_retryable', 0):,}", kategori="uyari")
    with c4:
        kpi_karti("Ortalama Yaş", f"{stats.get('ortalama_yas_saat', 0):.1f} saat", kategori="uyari")

    # --- Hata Türleri ---
    st.divider()
    st.subheader("Hata Türleri")
    if stats["hata_turleri"]:
        ht_df = pd.DataFrame(
            [{"Hata Türü": k, "Adet": v} for k, v in stats["hata_turleri"].items()],
        )
        ht_df = ht_df.sort_values("Adet", ascending=False)
        st.bar_chart(ht_df.set_index("Hata Türü"), width="stretch")
        st.dataframe(ht_df, width="stretch", hide_index=True)
    else:
        st.info("Hata türü bilgisi yok.")

    # --- Zaman Araligi ---
    st.divider()
    st.subheader("Zaman Aralığı")
    eski = stats.get("en_eski")
    yeni = stats.get("en_yeni")
    if eski and yeni:
        c1, c2 = st.columns(2)
        with c1:
            kpi_karti("En Eski", eski, kategori="uyari")
        with c2:
            kpi_karti("En Yeni", yeni, kategori="uyari")

    # --- DLQ Girdileri ---
    st.divider()
    st.subheader("DLQ Girdileri")
    if stats.get("entries"):
        rows = []
        for ev in stats["entries"]:
            rows.append({
                "Zaman": ev.get("timestamp", ""),
                "Hata Türü": ev.get("error_type", "unknown"),
                "Hata": ev.get("error", ""),
                "ActorRunId": (ev.get("payload") or {}).get("actorRunId", ""),
                "ActorId": (ev.get("payload") or {}).get("actorId", ""),
                "EventType": (ev.get("payload") or {}).get("eventType", ""),
            })
        df = pd.DataFrame(rows)
        st.dataframe(df, width="stretch", hide_index=True)

    # --- Retry Butonu ---
    st.divider()
    st.subheader("Retry İşlemleri")
    retryable = stats.get("retryable", 0)
    st.info(f"Tekrar denenebilir: {retryable} giriş (auth, rate limit hataları)")
    if st.button("🔄 Tüm Retry Güvenli Girdileri Tekrar Dene"):
        if retryable > 0:
            st.success(f"{retryable} giriş retry kuyruğuna alindi.")
        else:
            st.info("Tekrar denenebilir giriş yok.")

    st.caption("Son güncelleme: " + datetime.now().strftime("%Y-%m-%d %H:%M"))
