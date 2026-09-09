"""Orkestratör - İç Ajan Manifest'leri ve kayıt defteri.

İç ajan seti: koordinatör, mimar, araştırmacı, geliştirici, kalite, web_kazima.
Bu ajanlar proje köküne doğrudan erişir (harici ajanlardan farklı: workspace
izolasyonu yoktur). Orkestratör bunların görev sahipliğini, durumunu ve
dosya-lock'larını takip eder.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class IcAjanId(str, Enum):
    KOORDINATOR = "koordinator"
    MIMAR = "mimar"
    ARASTIRMACI = "arastirmaci"
    GELISTIRICI = "gelistirici"
    KALITE = "kalite"
    WEB_KAZIMA = "web_kazima"


@dataclass
class IcAjanManifest:
    """İç ajana görev atarken kullanılan tanım."""

    ajid: str
    display_name: str
    yetki_alanlari: list[str] = field(default_factory=list)
    kisitlar: list[str] = field(default_factory=list)
    erisim_notlari: str = ""
    aktif: bool = True


IC_AJANLAR: dict[str, IcAjanManifest] = {
    IcAjanId.KOORDINATOR.value: IcAjanManifest(
        ajid="koordinator",
        display_name="Koordinatör Ajan",
        yetki_alanlari=["orkestrasyon", "önceliklendirme", "işbölümü", "çakışma önleme"],
        kisitlar=["doğrudan kod üretmez; yönlendirir ve eşgüdüm yapar"],
        erisim_notlari="AGENTS.md, CLAUDE.md, V10/00-Home.md",
    ),
    IcAjanId.MIMAR.value: IcAjanManifest(
        ajid="mimar",
        display_name="Mimar Ajan",
        yetki_alanlari=["şema", "mimari kararlar", "ETL tasarımı", "micro-arch"],
        kisitlar=["implementation yerine tasarım odaklı"],
        erisim_notlari="V10/03_mimari, src/company_master/schema",
    ),
    IcAjanId.ARASTIRMACI.value: IcAjanManifest(
        ajid="arastirmaci",
        display_name="Araştırmacı Ajan",
        yetki_alanlari=["kaynak araştırma", "API inceleme", "KVKK/legal", "bilgi toplama"],
        kisitlar=["veri üretmez; doğrulanabilir kaynak arar"],
        erisim_notlari="V10/07_referanslar, scripts/mersis_api_research.md",
    ),
    IcAjanId.GELISTIRICI.value: IcAjanManifest(
        ajid="gelistirici",
        display_name="Geliştirici Ajan",
        yetki_alanlari=["kod", "scraper", "ETL implementasyonu", "test"],
        kisitlar=["mevcut çalışan sistemleri bozmadan çalışır"],
        erisim_notlari="src/company_master, scripts/",
    ),
    IcAjanId.KALITE.value: IcAjanManifest(
        ajid="kalite",
        display_name="Kalite Ajan",
        yetki_alanlari=["test coverage", "veri kalitesi KPI", "review", "doğrulama"],
        kisitlar=["üretmekten çok doğrular; gate görevi görür"],
        erisim_notlari="tests/, data/kpi_raporu.md",
    ),
    IcAjanId.WEB_KAZIMA.value: IcAjanManifest(
        ajid="web_kazima",
        display_name="Web Kazıma Uzmanı",
        yetki_alanlari=["kovaryans", "scrape", "robots.txt", "KVKK kazıma izni"],
        kisitlar=["izinli/kontrollü kazıma; rate-limit ve robots.txt uyar"],
        erisim_notlari="src/company_master/engine, src/company_master/utils",
    ),
}


def ic_ajanlar() -> dict[str, IcAjanManifest]:
    return dict(IC_AJANLAR)


def ic_ajan(ajid: str) -> IcAjanManifest | None:
    return IC_AJANLAR.get(ajid)