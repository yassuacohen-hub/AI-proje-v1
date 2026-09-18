# -*- coding: utf-8 -*-
"""P7-43: Hata Yonetimi sekmesi — Gercek hata kaynagi + rapor kaydi.

Ozellikler:
- Merkezi hata log dosyasindan (data/errors/error_log.jsonl) oku
- Hata turu, kaynak, seviye, zaman filtreleme
- Gercek istatistikler (son 24 saat / 7 gun / 30 gun)
- Hata raporlama formu (kullanici geri bildirimi)
- Hata detay gosterimi
"""
from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent.parent
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from company_master.logging.error_logger import (
    get_recent_errors,
    get_error_stats,
)

ERROR_COLORS = {
    "ERROR": "🔴",
    "WARNING": "🟠",
    "INFO": "🔵",
    "CRITICAL": "🟣",
    "DEBUG": "⚪",
}

LEVEL_ORDER = ["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"]


def _format_error_entry(entry: dict) -> str:
    """Hata kaydini okunabilir metne cevir."""
    ts = entry.get("timestamp", "")
    level = entry.get("level", "UNKNOWN")
    source = entry.get("source", "unknown")
    etype = entry.get("error_type", "UnknownError")
    msg = entry.get("message", "")
    ctx = entry.get("context", {})
    tb = entry.get("traceback", "")

    parts = [
        f"**{ERROR_COLORS.get(level, '⚪')} [{level}] {ts}**",
        f"**Kaynak:** {source}  |  **Tur:** {etype}",
        f"**Mesaj:** {msg}",
    ]
    if ctx:
        parts.append(f"**Baglam:** {ctx}")
    if tb:
        parts.append(f"**Stack Trace:**\n```\n{tb[:2000]}\n```")
    return "\n\n".join(parts)


def render_errors_tab() -> None:
    """Hata yonetimi sekmesini gosterir."""
    st.subheader("❌ Hata Yonetimi")

    # ---- Filtreler ----
    col1, col2, col3 = st.columns(3)
    with col1:
        level_filter = st.selectbox(
            "Seviye",
            ["Hepsi"] + LEVEL_ORDER,
            index=0,
            key="error_level_filter",
        )
    with col2:
        source_filter = st.selectbox(
            "Kaynak",
            ["Hepsi", "streamlit_tab", "fastapi", "orchestrator", "manual_test"],
            index=0,
            key="error_source_filter",
        )
    with col3:
        days_filter = st.selectbox(
            "Donem",
            ["Son 1 saat", "Son 24 saat", "Son 7 gun", "Son 30 gun", "Tumu"],
            index=1,
            key="error_days_filter",
        )

    # Donem -> gun sayisi
    days_map = {
        "Son 1 saat": 1/24,
        "Son 24 saat": 1,
        "Son 7 gun": 7,
        "Son 30 gun": 30,
        "Tumu": None,
    }
    days = days_map[days_filter]

    # ---- Hatalari getir ----
    level = None if level_filter == "Hepsi" else level_filter
    source = None if source_filter == "Hepsi" else source_filter

    errors = get_recent_errors(limit=200, level=level, source=source, days=days)

    # ---- Istatikler ----
    st.divider()
    st.subheader("📊 Hata Istatikleri")

    stats = get_error_stats(days=int(days) if days else 30)

    mcol1, mcol2, mcol3, mcol4 = st.columns(4)
    with mcol1:
        st.metric("Toplam Hata", stats["total"])
    with mcol2:
        st.metric("ERROR", stats["by_level"].get("ERROR", 0))
    with mcol3:
        st.metric("WARNING", stats["by_level"].get("WARNING", 0))
    with mcol4:
        st.metric("CRITICAL", stats["by_level"].get("CRITICAL", 0))

    # Kaynak dagilimi
    if stats["by_source"]:
        st.caption("**Kaynak dagilimi:**")
        src_cols = st.columns(min(len(stats["by_source"]), 4))
        for i, (src, count) in enumerate(stats["by_source"].items()):
            with src_cols[i % len(src_cols)]:
                st.metric(src, count)

    # Tur dagilimi
    if stats["by_type"]:
        st.caption("**Hata turu dagilimi:**")
        type_cols = st.columns(min(len(stats["by_type"]), 4))
        for i, (etype, count) in enumerate(stats["by_type"].items()):
            with type_cols[i % len(type_cols)]:
                st.metric(etype, count)

    # ---- Hata listesi ----
    st.divider()
    st.subheader(f"📋 Hata Listesi ({len(errors)} kayit)")

    if not errors:
        st.info("Seçili filtrelerde hata kaydi bulunamadi.")
    else:
        for i, entry in enumerate(errors):
            with st.expander(
                f"{ERROR_COLORS.get(entry.get('level', ''), '⚪')} "
                f"[{entry.get('level', '?')}] {entry.get('timestamp', '')} | "
                f"{entry.get('source', '?')} | {entry.get('error_type', '?')}",
                expanded=(i < 3),
            ):
                st.markdown(_format_error_entry(entry))

    # ---- Hata raporlama formu (kullanici geri bildirimi) ----
    st.divider()
    st.subheader("📝 Hata Raporu Gonder (Kullanici Geri Bildirimi)")

    with st.form("error_report_form"):
        reporter = st.text_input("Ad Soyad", placeholder="Adiniz")
        reporter_email = st.text_input("E-posta", placeholder="E-posta adresiniz")
        report_error_type = st.selectbox(
            "Hata Turu",
            [
                "UI/UX Hatasi",
                "Performans/Yukleme",
                "Veri/Goruntu Hatasi",
                "Giris/Yetki Hatasi",
                "Baska",
            ],
        )
        description = st.text_area(
            "Aciklama",
            placeholder="Hata ne zaman, hangi sayfada, hangi islemlerde olustu? Ekran goruntusu varsa tarif edin...",
            height=100,
        )
        submitted = st.form_submit_button("📤 Raporu Gonder", type="primary")

        if submitted:
            if not reporter.strip() or not description.strip():
                st.error("Ad soyad ve aciklama zorunludur.")
            else:
                from company_master.logging.error_logger import log_error_simple
                log_error_simple(
                    error_type=report_error_type,
                    message=description,
                    context={
                        "reporter": reporter,
                        "email": reporter_email,
                        "user_agent": "streamlit",
                    },
                    source="user_report",
                    level="WARNING",
                )
                st.success("✅ Hata raporu alindi! Tesekkur ederiz.")
                st.balloons()


if __name__ == "__main__":
    # Manuel test
    import tempfile

    # Test icin gecici log dosyasi olustur
    from company_master.logging.error_logger import ERROR_LOG_FILE, log_error
    try:
        raise ValueError("Test hatasi 1")
    except Exception as e:
        log_error(e, source="manual_test")

    try:
        raise ConnectionError("Test baglanti hatasi")
    except Exception as e:
        log_error(e, source="fastapi")

    print("Test loglari yazildi:", ERROR_LOG_FILE)
