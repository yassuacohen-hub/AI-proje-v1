#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, "src")
from company_master.orchestrator import task_board as tb

tb.gorev_guncelle("P0-1", durum="done", **{"not": "5485 firma detay scrape tamamlandi. Ingest ve pipeline tetiklendi."})
tb.handoff_yaz("P0-1", "OSTIM detay scrape tamamlandi (5485 firma)")

tb.gorev_guncelle("P0-2", durum="done", **{"not": "Syntax hatasi duzeltilip calistirildi. Ingest 5485/5485 matched, 0 errors. 43 VKN footer extract ile DB'ye yazildi."})
tb.handoff_yaz("P0-2", "Ingest + VKN + quality recalc + KPI tamamlandi")

tb.gorev_guncelle("P0-3", durum="aktif", **{"not": "Skor 7.23 -> 27.72. VKN eksikligi ana darboz. MERSIS API/OSB uyelik listesi gerekir."})

tb.agent_sync_yaz()
print("Task board updated!")
