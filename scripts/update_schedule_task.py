#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, "src")
from company_master.orchestrator import task_board as tb

# P2-3: Zamanlanmış scrape - script hazır
tb.gorev_guncelle("P2-3", durum="done", **{"not": "scheduled_scrape.py olusturuldu. Gunluk 02:00 scrape + watcher pipeline. Cron/systemd timer kurulumu bekliyor."})
tb.handoff_yaz("P2-3", "Zamanlanmis scrape scripti hazir", "Cron/timer kurulumu")

tb.agent_sync_yaz()
print("Guncellendi!")
