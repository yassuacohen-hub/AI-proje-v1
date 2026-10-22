# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, "src")
from company_master import chat

tid = "VERI-RAPIDAPI-OSINT-ISTEMCI-01"
kayitlar = chat.oku(tid)
print(f"toplam kayit: {len(kayitlar)}")
for i, k in enumerate(kayitlar):
    print(f"index={i} durum={k.get('durum')} ajan={k.get('ajan')} zaman={k.get('zaman') or k.get('tarih')}")
    print(f"   sorun: {str(k.get('sorun'))[:90]}")
