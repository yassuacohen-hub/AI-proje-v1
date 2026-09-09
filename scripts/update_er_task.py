#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, "src")
from company_master.orchestrator import task_board as tb

# P2-4: Entity resolution - threshold test completed
tb.gorev_guncelle("P2-4", durum="aktif", **{"not": "Rapidfuzz kullanilarak threshold optimizasyonu yapildi. Mevcut sistem SequenceMatcher (0.85) kullaniyor. Rapidfuzz daha iyi sonuclar veriyor. Threshold 0.8 oneriliyor."})

tb.agent_sync_yaz()
print("Guncellendi!")
