# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, "src")
from company_master import chat

tid = "VERI-RAPIDAPI-OSINT-ISTEMCI-01"
print("=== teslim_kontrol_et (ajan-chat.jsonl) ===")
try:
    aciklar = chat.teslim_kontrol_et(tid)
    if aciklar is None:
        print("  (None dondu)")
    else:
        print(f"  {len(aciklar)} acik kayit")
        for k in aciklar:
            print("   -", repr(k)[:220])
except Exception as e:
    print("  HATA:", type(e).__name__, e)
