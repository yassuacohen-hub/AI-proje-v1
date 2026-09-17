"""DASH-08: Admin Denetim (Audit) Sekmesi.

Denetim kayitlari:
  - Karar Defteri (Decision Log)
  - Dosya Kilidi Durumu
  - Handoff Logu
  - Görev Durum Özeti
  - Trigger Logu
"""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

from web_dashboard.charts import kpi_karti  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "src"))

from company_master.i18n import t  # noqa: E402
from company_master.orchestrator import task_board as tb
from scripts.decision_log import read_decisions

FILE_LOCKS = ROOT / "data" / "orchestrator" / "file_locks.json"
HANDOFFS = ROOT / "data" / "orchestrator" / "handoffs.json"
TRIGGER_LOG = ROOT / "data" / "orchestrator" / "trigger_log.jsonl"


# ---------------------------------------------------------------------------
# Veri Yükleme Fonksiyonları
# ---------------------------------------------------------------------------


@st.cache_data(ttl=30)
def load_file_locks() -> dict[str, Any]:
    if FILE_LOCKS.exists():
        try:
            data = json.loads(FILE_LOCKS.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data
        except (json.JSONDecodeError, OSError, TypeError, ValueError):
            return {}
    return {}


@st.cache_data(ttl=30)
def load_handoffs() -> dict[str, Any]:
    if HANDOFFS.exists():
        try:
            data = json.loads(HANDOFFS.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return data
        except (json.JSONDecodeError, OSError, TypeError, ValueError):
            return {}
    return {}


@st.cache_data(ttl=30)
def load_trigger_log() -> list[dict[str, Any]]:
    if not TRIGGER_LOG.exists():
        return []
    entries: list[dict[str, Any]] = []
    for line in TRIGGER_LOG.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entries.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return entries


# ---------------------------------------------------------------------------
# Render Fonksiyonları
# ---------------------------------------------------------------------------


def render_audit_tab() -> None:
    """DASH-08: Admin Denetim (Audit) sekmesi."""

    st.subheader("🔍 Admin Denetim")
    st.caption(t("muninn_audit_trail_ready") + " — son güncelleme: " + datetime.now().strftime("%Y-%m-%d %H:%M"))

    # --- Karar Defteri ---
    st.divider()
    st.subheader("📋 Karar Defteri (Decision Log)")

    decisions = read_decisions(limit=30)
    if decisions:
        rows = []
        for d in decisions:
            tags = d.get("tags", [])
            if not isinstance(tags, list):
                tags = [str(etiket) for etiket in tags]
            rows.append({
                "Tarih": d.get("ts", ""),
                "Başlık": d.get("title", ""),
                "Karar": d.get("decision", ""),
                "Karar Vereren": d.get("decider", ""),
                "Gerekçe": d.get("reason", ""),
                "Etiketler": ", ".join(str(etiket) for etiket in tags),
            })
        df = pd.DataFrame(rows)
        st.dataframe(df, width="stretch", hide_index=True)
        st.caption(f"Toplam {len(decisions)} karar kaydı gösteriliyor (son 30).")
    else:
        st.info("Henüz karar kaydı yok.")

    # --- Dosya Kilidi Durumu ---
    st.divider()
    st.subheader("🔒 Dosya Kilidi Durumu")

    locks = load_file_locks()
    if locks:
        lock_rows = []
        for fpath, info in locks.items():
            lock_rows.append({
                "Dosya": fpath,
                "Sahip": info.get("sahip", ""),
                "Görev": info.get("task_id", ""),
                "Kilitlendi": info.get("kilitlendi", ""),
            })
        lock_df = pd.DataFrame(lock_rows)
        st.dataframe(lock_df, width="stretch", hide_index=True)
        st.caption(f"Aktif kilitle: {len(locks)} dosya.")
    else:
        st.success("✅ Aktif dosya kilidi yok — tüm dosyalar serbest.")

    # --- Handoff Logu ---
    st.divider()
    st.subheader("🤝 Handoff Logu")

    handoffs = load_handoffs()
    if handoffs:
        hf_rows = []
        for tid, info in handoffs.items():
            hf_rows.append({
                "Görev": tid,
                "Tamamlandı": (info.get("tamamlandi") or "")[:100],
                "Sonraki Adım": (info.get("sonraki_adim") or "")[:80],
                "Tarih": info.get("tarih", ""),
            })
        hf_df = pd.DataFrame(hf_rows)
        st.dataframe(hf_df, width="stretch", hide_index=True)
        st.caption(f"Toplam {len(handoffs)} handoff kaydı.")
    else:
        st.info("Henüz handoff kaydı yok.")

    # --- Görev Durum Özeti ---
    st.divider()
    st.subheader("📊 Görev Durum Özeti")

    try:
        board = tb.gorev_listesi()
        if board:
            status_counts: dict[str, int] = {}
            for gorev in board:
                durum = gorev.get("durum", "unknown")
                status_counts[durum] = status_counts.get(durum, 0) + 1

            c1, c2, c3, c4, c5 = st.columns(5)
            with c1:
                kpi_karti("Toplam Görev", len(board), kategori="guvenlik")
            with c2:
                kpi_karti("✅ Done", status_counts.get("done", 0), kategori="guvenlik")
            with c3:
                kpi_karti("🔵 Aktif", status_counts.get("aktif", 0), kategori="guvenlik")
            with c4:
                kpi_karti("🟡 Review", status_counts.get("review", 0), kategori="guvenlik")
            with c5:
                kpi_karti("🔴 Blocked", status_counts.get("blocked", 0), kategori="guvenlik")
            task_df = pd.DataFrame([
                {
                    "Görev ID": gorev.get("task_id", ""),
                    "Başlık": (gorev.get("baslik") or gorev.get("title", ""))[:60],
                    "Sahip": gorev.get("sahip", ""),
                    "Öncelik": gorev.get("oncelik", ""),
                    "Durum": gorev.get("durum", ""),
                }
                for gorev in board
            ])
            st.dataframe(task_df, width="stretch", hide_index=True)
        else:
            st.info("Görev verisi bulunamadı.")
    except Exception as e:
        st.warning(f"Görev durumu yüklenemedi: {e}")

    # --- Trigger Logu ---
    st.divider()
    st.subheader("⚡ Trigger Logu")

    triggers = load_trigger_log()
    if triggers:
        tr_rows = []
        for tetik in triggers[-20:]:
            tr_rows.append({
                "Zaman": tetik.get("ts", ""),
                "Kaynak": tetik.get("kaynak", ""),
                "Ajan": tetik.get("ajan", ""),
                "Görev": tetik.get("task_id", ""),
                "Tetik Sayısı": tetik.get("tetik_sayisi", 0),
            })
        tr_df = pd.DataFrame(tr_rows)
        st.dataframe(tr_df, width="stretch", hide_index=True)
        st.caption(f"Son {len(triggers)} trigger kaydı gösteriliyor.")
    else:
        st.info("Trigger kaydı yok.")
