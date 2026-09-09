#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, "src")
from company_master.orchestrator import task_board as tb

# P1-4: Multi-OSB merger - completed
tb.gorev_guncelle("P1-4", durum="done", **{"not": "Merger tamamlandi. 6270 kayit -> 5756 firma. OSTIM+ASO birlestirildi. merged_companies.jsonl kaydedildi."})
tb.handoff_yaz("P1-4", "Multi-OSB merger tamamlandi (5756 firma)", "Merged veri DB'ye yazilabilir")

# P1-1: İvedik scraper
tb.gorev_guncelle("P1-1", durum="aktif", **{"not": "Scraper iskeleti hazir. Veri dosyasi olusturulmadi, henüz implementasyon yapilmadi."})

# P1-2: Başkent scraper
tb.gorev_guncelle("P1-2", durum="aktif", **{"not": "Scraper iskeleti hazir. Veri dosyasi olusturulmadi, henüz implementasyon yapilmadi."})

tb.agent_sync_yaz()
print("Guncellendi!")
