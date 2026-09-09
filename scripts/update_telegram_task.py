#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, "src")
from company_master.orchestrator import task_board as tb

tb.gorev_guncelle("P1-6", durum="done", **{"not": "Telegram bot aktif. Dashboard: http://localhost:8503. Canli rapor gonderiliyor."})
tb.handoff_yaz("P1-6", "Telegram bot tamamlandi", "Canli durum raporu aktif")
tb.agent_sync_yaz()
print("Guncellendi!")
