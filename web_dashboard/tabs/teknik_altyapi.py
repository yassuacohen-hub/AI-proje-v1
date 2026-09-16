# -*- coding: utf-8 -*-
"""KPI-EXA-02: Teknik Altyapı sayfası — süreç diyagramı ve servis haritası.

Sahip talebi (2026-09-15): Veri Akışı diyagramı Ana Kontrol'de "ilk görülecek
yer" değildi; teknik altyapı diyagramları/bilgileri **tek ayrı sayfada** toplanır.
Düğümler kısa BÜYÜK HARF (KAYNAK → EŞLEŞTİRME → VERİTABANI → API → DASHBOARD),
çerçeve hafif kırık beyaz, boyut küçük.
"""
from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT / "src"))

from company_master.ui import PageHeader, Section, SectionNav  # noqa: E402
from web_dashboard.charts import VERI_AKISI_VARSAYILAN, veri_akisi  # noqa: E402

BOLUMLER: tuple[Section, ...] = (
    Section("Veri Akışı", kimlik="veri-akisi"),
    Section("Servisler", kimlik="servisler"),
)

#: Servis haritası — (ad, port/konum, rol). Gizli bilgi içermez.
SERVISLER: tuple[tuple[str, str, str], ...] = (
    ("Huginn API", ":8000 (Docker)", "FastAPI — müşteri yüzeyi, /api/*"),
    ("Muninn Panel", ":8501", "Streamlit — iç ekip paneli"),
    ("Veritabanı", "PostgreSQL", "companies, users, signals"),
    ("Webhook Alıcı", "/api/webhooks/apify", "Apify olayları, DLQ"),
)


def _bolum(kimlik: str) -> Section:
    for bolum in BOLUMLER:
        if bolum.kimlik == kimlik:
            return bolum
    raise KeyError(f"Tanımsız bölüm kimliği: {kimlik}")


def akis_metni(dugumler=VERI_AKISI_VARSAYILAN) -> str:
    """Diyagramın metin karşılığı (erişilebilirlik + graphviz yoksa)."""
    return " → ".join(ad for _, ad, _ in dugumler)


def render_teknik_altyapi_tab() -> None:
    """Teknik Altyapı sayfası: süreç diyagramı + servis tablosu."""
    PageHeader(
        "Teknik Altyapı",
        giris="Verinin kaynaktan panele izlediği yol ve çalışan servisler.",
        ust_etiket="Sistem",
    ).render()
    SectionNav(BOLUMLER, yatay=True).render()

    _bolum("veri-akisi").render()
    veri_akisi()
    st.caption(akis_metni())

    _bolum("servisler").render()
    st.table(
        [{"Servis": ad, "Konum": konum, "Rol": rol} for ad, konum, rol in SERVISLER]
    )
