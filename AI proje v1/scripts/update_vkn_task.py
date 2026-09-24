#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, "src")
from company_master.orchestrator import task_board as tb

# P1-7: VKN web kazima - in progress
tb.gorev_guncelle("P1-7", durum="aktif", **{"not": "Pilot 2 tamamlandi: 30 site tarandi. 0 VKN bulundu, VPN/robots.txt engelleri loglandi. Strateji ve araclar hazir."})

tb.agent_sync_yaz()
print("Guncellendi!")
