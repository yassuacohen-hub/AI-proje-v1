#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, "src")
from company_master.orchestrator import task_board as tb

# P1-5: NACE eksikleri - in progress
tb.gorev_guncelle("P1-5", durum="aktif", **{"not": "582 firmanin NACE'si sektor field'indan dolduruldu. Kalan 684 firma icin farkli kaynaklar aranacak."})
tb.handoff_yaz("P1-5", "NACE eksikleri azaltildi (582/1266)", "Kalan 684 firma icin arastirma devam ediyor")

tb.agent_sync_yaz()
print("Guncellendi!")
