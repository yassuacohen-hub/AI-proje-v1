#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, "src")
from company_master.orchestrator import task_board as tb

# P1-5: NACE eksikleri - progress
tb.gorev_guncelle("P1-5", durum="aktif", **{"not": "582/1266 NACE dolduruldu (sektor field'indan). Kalan 684 firma manuel arastirma gerektiriyor."})

# P2-3: Zamanlanmış scrape - start planning
tb.gorev_guncelle("P2-3", durum="aktif", **{"not": "Cron/timer kurulumu planlaniyor. Scrape watchdog + post_scrape_workflow pipeline ile entegre edilecek."})

tb.agent_sync_yaz()
print("Guncellendi!")
