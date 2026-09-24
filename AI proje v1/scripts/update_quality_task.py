#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, "src")
from company_master.orchestrator import task_board as tb

# P0-3: Quality score - in progress
tb.gorev_guncelle("P0-3", durum="aktif", **{"not": "Skor 30.36 -> 39.97. VKN cezasi -5 yapildi. ASO'da email 3668 firma bulundu ancak VPN nedeniyle DB erisimi kesildi, doldurma yapilamadi. Hedef 50+."})

# Note VPN issue
tb.handoff_yaz("P0-3", "Kalite skoru 39.97'a yukseltildi", "VPN sorunu nedeniyle DB erisimi yok. Cozuldugunde email/VKN doldurma devam edecek.")

tb.agent_sync_yaz()
print("Guncellendi!")
