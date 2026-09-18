# -*- coding: utf-8 -*-
"""P7-43: Hata sayfalari — 404, 500, baglanti hatasi icin kullanici dosyalar.

Hata yönetimi UX:
- 404 (Bulunamadi) hata sayfası
- 500 (Sunucu Hatasi) hata sayfası
- Bağlantı hatasi kullanici dosyasi
- Hata raporlama
- Hata izleme logu
"""
from __future__ import annotations

import json
import os
import sys
import traceback
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "src"))

ERROR_COLORS = {
    "error": "🔴",
    "warning": "🟠",
    "info": "🔵",
    "success": "🟢",
}

ERROR_TEMPLATES = {
    "404": {
        "title": "404 — Bulunamadı",
        "message": "İstenen sayfa veya kaynak bulunamadı. Lütfen adresi kontrol edin.",
        "icon": "🔍",
        "color": "warning",
    },
    "500": {
        "title": "500 — Sunucu Hatası",
        "message": "Bir hata oluştu. Lütfen daha sonra tekrar deneyin. Sorun devam ederse yönetimi bilgilendirin.",
        "icon": "🔧",
        "color": "error",
    },
    "connection": {
        "title": "Bağlantı Hatası",
        "message": "Sunucuya bağlanılamıyor. Ağ ayarlarınızı ve VPN durumunuzu kontrol edin.",
        "icon": "🌐",
        "color": "error",
    },
    "timeout": {
        "title": "Zaman Aşımı",
        "message": "İşlem tamamlanamadı. Daha sonra tekrar deneyin veya zaman aşımını artırın.",
        "icon": "⏱️",
        "color": "warning",
    },
    "permission": {
        "title": "İzin Reddedildi",
        "message": "Bu kaynağa erişim yetkiniz bulunmuyor. Yetkilendirmenizi kontrol edin.",
        "icon": "🔒",
        "color": "error",
    },
}


def _save_error_report(report: dict) -> None:
    """Hata raporunu JSONL dosyasına kaydeder."""
    errors_dir = ROOT / "data" / "errors"
    errors_dir.mkdir(parents=True, exist_ok=True)
    report_file = errors_dir / "error_reports.jsonl"
    with report_file.open("a", encoding="utf-8") as f:
        f.write(json.dumps(report, ensure_ascii=False) + "\n")


def render_error_page(error_code: str, details: str = "") -> None:
    """Hata sayfası gösterir."""
    template = ERROR_TEMPLATES.get(error_code, ERROR_TEMPLATES["404"])
    color = template["color"]

    st.error(f"{template['icon']} **{template['title']}**", icon=template["icon"])
    st.info(template["message"])

    if details:
        with st.expander("Detaylar"):
            st.code(details, language="text")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("🏠 Ana Sayfaya Dön", type="primary", width="stretch"):
            st.rerun()
    with col2:
        if st.button("📧 Destek İletişimi", width="stretch"):
            st.info("Destek ekibimize haber verin: destek@huginn.local")


def render_errors_tab() -> None:
    """Hata yönetimi sekmesini gösterir."""
    st.subheader("❌ Hata Yönetimi")

    st.divider()
    st.subheader("📋 Hata Türleri")

    error_type = st.selectbox(
        "Hata Türü",
        list(ERROR_TEMPLATES.keys()),
        format_func=lambda x: f"{x} — {ERROR_TEMPLATES[x]['title']}",
        key="error_type_select",
    )

    if st.button("▶️ Hata Sayfasını Görüntüle", type="primary", width="stretch"):
        render_error_page(error_type)

    st.divider()
    st.subheader("🧪 Hata Simülasyonu (Geliştirici Modu)")

    demo = st.radio(
        "Demo",
        ["Simüle 404", "Simüle 500", "Simüle Bağlantı Hatası"],
        horizontal=True,
        key="error_demo",
    )

    if st.button("🔥 Hatayı Simüle Et", type="primary", width="stretch"):
        if "404" in demo:
            raise ValueError("404 — Simüle hata")
        elif "500" in demo:
            raise RuntimeError("500 — Simüle sunucu hatası")
        else:
            raise ConnectionError("Bağlantı hatası — simüle")

    st.divider()
    st.subheader("📝 Hata Raporu")

    with st.form("error_report"):
        reporter = st.text_input("Ad Soyad", placeholder="Adınız")
        reporter_email = st.text_input("E-posta", placeholder="E-posta adresiniz")
        report_error = st.selectbox("Hata Türü", list(ERROR_TEMPLATES.keys()))
        description = st.text_area("Açıklama", placeholder="Hata açıklaması...")
        submitted = st.form_submit_button("📤 Raporu Gönder", type="primary")

        if submitted:
            timestamp = datetime.now().isoformat()
            report = {
                "tarih": timestamp,
                "raporlayan": reporter,
                "email": reporter_email,
                "hata_turu": report_error,
                "aciklama": description,
                "durum": "kayit_edildi",
            }
            _save_error_report(report)
            st.success(f"✅ Hata raporu alındı! ({timestamp})")
            st.json(report)

    st.divider()
    st.subheader("📊 Hata İstatistikleri")

    st.info("Gerçek hata istatistikleri için veri kaynağı bağlanmalıdır. Şu an için örnek veriler gösterilmektedir.")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("404", "—", delta="Veri yok")
    with col2:
        st.metric("500", "—", delta="Veri yok")
    with col3:
        st.metric("Bağlantı", "—", delta="Veri yok")

    st.caption("Dönem: Son 24 saat — Gerçek veri kaynağı entegrasyonu bekleniyor.")
