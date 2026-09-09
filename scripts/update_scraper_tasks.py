#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, "src")
from company_master.orchestrator import task_board as tb

# P1-1: İvedik - VPN/DNS engeli nedeniyle askıda
tb.gorev_guncelle("P1-1", durum="plan", **{"not": "VPN/DNS engeli nedeniyle ivedik.org.tr erisim saglanamadi. Erisim saglandiginda scraper implementasyonu yapilacak."})

# P1-2: Başkent - VPN/DNS engeli nedeniyle askıda
tb.gorev_guncelle("P1-2", durum="plan", **{"not": "VPN/DNS engeli nedeniyle baskentosb.org.tr erisim saglanamadi. Erisim saglandiginda scraper implementasyonu yapilacak."})

tb.agent_sync_yaz()
print("Guncellendi!")
