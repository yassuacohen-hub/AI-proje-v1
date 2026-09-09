# -*- coding: utf-8 -*-
"""Pano guncelleme: P1-5 NACE tamam, P2-4 threshold analizi, P2-3 dokumani."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from company_master.orchestrator import task_board as tb  # noqa: E402

# P1-5 NACE tamam
tb.gorev_guncelle("P1-5", durum="done", **{
    "not": ("nace_eksik_doldur.py calistirildi: 634 NACE'siz firma dolduruldu. "
            "Sonuc: NACE 9007/9007 (%100). Kaynak dagilimi: fallback 612, "
            "title_default 22. Mevcut 0.85 threshold ile devam (P2-4 analizi).")
})
tb.handoff_yaz("P1-5", "NACE %100 (9007/9007) - 634 yeni doldurma",
               "Kalite skoru recalc (P0-3) ve entity resolution (P2-4) kaldi")

# P2-4 threshold analizi tamam
tb.gorev_guncelle("P2-4", durum="done", **{
    "not": ("entity_resolution_benchmark: 50x500 orneklemle threshold analizi. "
            "Mevcut 0.85 dengeli (0.80 agresif, 0.75 cok agresif). "
            "Mevcut entity_resolution: 8313 new, 583 possible_match, 9 vkn_exact. "
            "Threshold 0.85'te kalinsin.")
})
tb.handoff_yaz("P2-4", "Threshold 0.85 onaylandi (benchmark ile)",
               "Yeni source_record gelistiginde run_entity_resolution calistir")

# P2-3 zamanli scrape dokumani hazir
tb.gorev_guncelle("P2-3", durum="aktif", **{
    "not": ("docs/P2-3_zamanli_scrape.md hazir: systemd timer + Windows Task Scheduler "
            "sablonlari. refresh_all_scrapers.py/service/timer/bat dosyalari eklenmesi kaldi.")
})
tb.handoff_yaz("P2-3", "Zamanli scrape dokumani + sablonlar hazir",
               "refresh_all_scrapers.py ve .service/.timer/.bat dosyalari eklenmeli")

# P1-7 VKN pilotu tamam
tb.gorev_guncelle("P1-7", durum="done", **{
    "not": ("vkn_web_scraper.py pilot tamamlandi: 30 site tarandi, 0 VKN bulundu "
            "(10 robots engelli, 20'de vergi no yok). Kucuk firmalar footer'da "
            "VKN gostermiyor. Strateji dokumani: 07_referanslar/vkn_bulma_stratejisi.md. "
            "Oneri: MERSIS API (P2-1) veya GIB vkn.gov.tr one cikar.")
})
tb.handoff_yaz("P1-7", "VKN web pilotu: 0/30 (dusuk verim, beklenen)",
               "MERSIS API basvurusu (P2-1) one cikar; web kazimi ikincil kaynak")

tb.agent_sync_yaz()
print("Pano guncellendi")