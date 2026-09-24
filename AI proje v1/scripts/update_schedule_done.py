#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, "src")
from company_master.orchestrator import task_board as tb

# P2-3: Zamanlanmış scrape - completed
tb.gorev_guncelle("P2-3", durum="done", **{"not": "scheduled_scrape.py + setup_daily_scrape.ps1/.bat hazir. Windows Task Scheduler ile 02:00'de gunluk scrape + watcher + post_scrape workflow calisir."})
tb.handoff_yaz("P2-3", "Zamanlanmis scrape tamamlandi", "PowerShell script ile kurulum yapilabilir")

tb.agent_sync_yaz()
print("Guncellendi!")
