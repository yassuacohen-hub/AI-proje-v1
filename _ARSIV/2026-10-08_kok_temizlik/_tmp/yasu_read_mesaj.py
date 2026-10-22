# -*- coding: utf-8 -*-
import json, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
BASE = r"c:\HUGINN~1\HUGINN~1"
yol = BASE + r"\data\orchestrator\chat\messages.jsonl"
import os
if not os.path.exists(yol):
    # bul
    for root, dirs, files in os.walk(BASE):
        if "messages.jsonl" in files:
            yol = os.path.join(root, "messages.jsonl")
            print("BULUNDU:", yol)
            break
TID = "VERI-RAPIDAPI-OSINT-ISTEMCI-01"
print("=== messages.jsonl cevapsiz kayitlar (VERI-RAPIDAPI) ===")
with open(yol, encoding="utf-8", errors="replace") as f:
    for idx, satir in enumerate(f):
        try:
            k = json.loads(satir)
        except Exception:
            continue
        if k.get("task_id") == TID and not k.get("yanit_alindi") and k.get("kimden") != "yasu":
            print(f"  index={idx} kimden={k.get('kimden')} kime={k.get('kime')} tarih={k.get('tarih')}")
            print(f"    mesaj: {str(k.get('mesaj',''))[:200]}")
