# -*- coding: utf-8 -*-
"""OSINT Scraper Motoru — kaynak kayit defteri.

Her veri kaynagi tek bir SourceSpec ile tanimlanir: scraper modulu, cikti
dosyasi, hedef domain ve pipeline baglantilari. Motor (osint_engine) bu
kayitlar uzerinden calisir.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]


@dataclass
class SourceSpec:
    """Tek bir OSINT veri kaynagi tanimi."""

    source_id: str                      # "ostim", "aso", "ivedik"...
    display_name: str                   # "OSTIM Uye Rehberi"
    domain: str                         # birincil domain (router politika anahtari)
    scraper_module: str | None = None   # "company_master.etl.scrapers.aso_scraper"
    scraper_cli: str | None = None      # python ile calistirilacak script yolu (ROOT'e gore)
    output_file: str = ""               # ROOT'e gore JSONL cikti
    pipeline: bool = True               # bitince ingest->VKN->recalc->KPI calisir mi
    enabled: bool = True
    note: str = ""

    @property
    def output_path(self) -> Path:
        return ROOT / self.output_file

    @property
    def scraper_cli_path(self) -> Path | None:
        return ROOT / self.scraper_cli if self.scraper_cli else None


def default_sources() -> list[SourceSpec]:
    """Projedeki bilinen kaynaklar (V10/10_ankara_osb_sentez.md + merger plani + job intelligence)."""
    return [
        SourceSpec(
            source_id="ostim-detail",
            display_name="OSTIM Detay Uye Scrape",
            domain="www.ostim.org.tr",
            scraper_cli="src/company_master/etl/scrapers/ostim_scraper.py",
            output_file="data/ostim/firmalar_detayli.jsonl",
            pipeline=True,
            note="17 sektor, ~8313 firma; detayli modda calisir",
        ),
        SourceSpec(
            source_id="ostim-list",
            display_name="OSTIM Liste (tamamlanmis)",
            domain="www.ostim.org.tr",
            scraper_cli=None,
            output_file="data/ostim/firmalar_full.jsonl",
            pipeline=False,
            note="Temel liste; NACE doluluk %84.8",
        ),
        SourceSpec(
            source_id="aso",
            display_name="ASO Firma Rehberi",
            domain="www.aso.org.tr",
            scraper_module="company_master.etl.scrapers.aso_scraper",
            scraper_cli=None,
            output_file="data/aso/aso_full.jsonl",
            pipeline=True,
            note="API tabanli (csrfToken); ~2000 firma hedefi",
        ),
        SourceSpec(
            source_id="ivedik",
            display_name="Ivedik OSB",
            domain="www.ivedikosb.org.tr",
            scraper_module=None,
            scraper_cli=None,
            output_file="data/ivedik/ivedik_full.jsonl",
            pipeline=True,
            enabled=False,
            note="PLANLI — scraper yazilacak (Web Kazima Uzmani)",
        ),
        SourceSpec(
            source_id="baskent",
            display_name="Baskent OSB",
            domain="www.baskentosb.org.tr",
            scraper_module=None,
            scraper_cli=None,
            output_file="data/baskent/baskent_full.jsonl",
            pipeline=True,
            enabled=False,
            note="PLANLI — scraper yazilacak (Web Kazima Uzmani)",
        ),
        # ============================================================
        # JOB INTELLIGENCE KAYNAKLARI
        # ============================================================
        SourceSpec(
            source_id="company-career-pages",
            display_name="Şirket Kariyer Sayfaları",
            domain="auto",  # Dinamik: companies.website_domain'den
            scraper_module="company_master.intelligence.job_intelligence.sources.company_career",
            output_file="data/job_intelligence/company_career_jobs.jsonl",
            pipeline=True,
            enabled=True,
            note="Mevcut 5000+ companies.website_domain'lerden otomatik keşif; KVKK güvenli",
        ),
        SourceSpec(
            source_id="iskur",
            display_name="İŞKUR Resmi İş İlanları",
            domain="www.iskur.gov.tr",
            scraper_module="company_master.intelligence.job_intelligence.sources.iskur",
            output_file="data/job_intelligence/iskur_jobs.jsonl",
            pipeline=True,
            enabled=True,
            note="Resmi istihdam kurumu; KVKK güvenli; yapılandırılmış veri",
        ),
        SourceSpec(
            source_id="kariyer-net",
            display_name="Kariyer.net İş İlanları",
            domain="www.kariyer.net",
            scraper_module="company_master.intelligence.job_intelligence.sources.kariyer_net",
            output_file="data/job_intelligence/kariyer_net_jobs.jsonl",
            pipeline=True,
            enabled=False,  # Anti-bot koruması için önce manuel test
            note="Türkiye'nin en büyük iş ilanı sitesi; sektör/şehir filtreli arama",
        ),
    ]


def registry() -> dict[str, SourceSpec]:
    """source_id -> SourceSpec haritasi."""
    return {s.source_id: s for s in default_sources()}
