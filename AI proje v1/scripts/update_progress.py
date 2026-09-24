#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, "src")
from company_master.orchestrator import task_board as tb

# P1-3: ASO ingest - completed
tb.gorev_guncelle("P1-3", durum="done", **{"not": "ASO ingest tamamlandi. 785 kayit, 0 hata. 159 yeni firma eklendi. 783 adres, 785 VKN yazildi."})
tb.handoff_yaz("P1-3", "ASO ingest tamamlandi (785 kayit)", "Kalite skoru 27.72 -> 30.36")

# P0-3: Quality score - in progress
tb.gorev_guncelle("P0-3", durum="aktif", **{"not": "Skor 27.72 -> 30.36. ASO ingest ile 783 adres ve 785 VKN eklendi. Hedef 50+ icin daha fazla VKN ve adres gerekli."})

# P1-1: İvedik scraper
tb.gorev_guncelle("P1-1", durum="aktif", **{"not": "Scraper iskeleti hazir, VPN ile test edilecek."})

# P1-2: Başkent scraper
tb.gorev_guncelle("P1-2", durum="aktif", **{"not": "Scraper iskeleti hazir, VPN ile test edilecek."})

tb.agent_sync_yaz()
print("Guncellendi!")
