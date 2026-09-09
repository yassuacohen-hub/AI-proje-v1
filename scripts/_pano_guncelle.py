# -*- coding: utf-8 -*-
"""Pano guncelleme: P1-4 ingest tamam; P1-7 VKN pilot suruyor."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from company_master.orchestrator import task_board as tb  # noqa: E402

tb.gorev_guncelle("P1-4", durum="done", **{
    "not": ("multi_osb_merger.py + ingest_merged_bulk.py calistirildi. "
            "Merged 5665 kayit -> DB: 80 yeni eklendi, 5585 guncellendi. "
            "Bulk upsert (tek sorgu/250 kayit) DB roundtrip 8sn sorununu cozdu: "
            "satir satir yerine ~25 sorguyla tamamlandi. Toplam: 9007 firma, "
            "NACE 7741 (%85.9), web 5061.")
})
tb.gorev_guncelle("P1-7", durum="aktif", **{
    "not": ("vkn_web_scraper.py pilot 2: 30 site taranacak. Ilk 13 sitede 0 VKN "
            "cikti (checksum dogrulama calisiyor, VPN kaynakli robots/DNS engelleri "
            "loglandi). Strateji + araclar hazir: 07_referanslar/vkn_bulma_stratejisi.md.")
})
tb.handoff_yaz(
    "P1-4",
    "Multi-OSB merged 5665 kayit DB'ye islendi (9007 toplam)",
    "Sira: NACE eksik 1266 firma (P1-5) ve kalite recalc (P0-3)",
)
tb.handoff_yaz(
    "P1-7",
    "VKN web pilotu suruyor (13/30 sitesi tamam, 0 VKN)",
    "Pilot bitince verim raporu; verim dusukse web disi kaynaklara gec (vkn_bulma_stratejisi.md bolum 7)",
)
tb.agent_sync_yaz()
print("Pano guncellendi")