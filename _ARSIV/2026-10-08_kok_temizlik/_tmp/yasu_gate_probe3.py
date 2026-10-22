# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, "src")
from company_master import chat

tid = "VERI-RAPIDAPI-OSINT-ISTEMCI-01"
sonuc = chat.teslim_kontrol_et(tid)
print("engel:", sonuc.get("engel"))
print("nedenler:")
for n in sonuc.get("nedenler", []):
    print("   -", repr(n)[:400])
