#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, "src")
from company_master.orchestrator import task_board as tb

# P2-4: Entity resolution - completed with rapidfuzz
tb.gorev_guncelle("P2-4", durum="done", **{"not": "Rapidfuzz ile threshold optimizasyonu tamamlandi. 592 kayit islendi: 9 VKN exact, 583 fuzzy match (0.80 threshold). SequenceMatcher (0.85) yerine rapidfuzz kullaniliyor."})
tb.handoff_yaz("P2-4", "Entity resolution rapidfuzz ile optimize edildi", "592 kayit eslesti")

tb.agent_sync_yaz()
print("Guncellendi!")
