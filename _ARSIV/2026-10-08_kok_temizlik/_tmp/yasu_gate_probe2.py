# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, "src")
from company_master import chat

tid = "VERI-RAPIDAPI-OSINT-ISTEMCI-01"
print("=== teslim_kontrol_et (ajan-chat.jsonl) ===")
aciklar = chat.teslim_kontrol_et(tid)
print("  tip:", type(aciklar).__name__, "| len:", len(aciklar) if aciklar else aciklar)
for k in aciklar:
    print("  KAYIT:", repr(k))

print()
print("=== _mesaj_kontrol_et (messages.jsonl) ===")
try:
    m = chat._mesaj_kontrol_et(tid)
    print("  tip:", type(m).__name__)
    print("  DEGER:", repr(m)[:800])
except Exception as e:
    print("  HATA:", type(e).__name__, e)
