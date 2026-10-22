# -*- coding: utf-8 -*-
"""RAPIDAPI acik kayitlarin TAM icerigi + messages.jsonl kaynakli mesajlar."""
import sys, json
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, str(Path(r"c:\HUGINN~1\HUGINN~1\src")))
from company_master import chat

TASK = "VERI-RAPIDAPI-OSINT-ISTEMCI-01"
print("=== chat.jsonl (ajan-chat) acik kayitlar ===")
for i, s in enumerate(chat.oku(task_id=TASK)):
    if s.get("durum") == "acik":
        print(f"\n[{i}] kimden={s.get('kimden')} onem={s.get('onem')}")
        print(f"  SORUN: {s.get('sorun')}")
        print(f"  COZUM: {s.get('cozum') or '(bos)'}")

msg_path = Path(r"c:\HUGINN~1\HUGINN~1\data\orchestrator\messages.jsonl")
print(f"\n\n=== messages.jsonl: {msg_path.exists()} ===")
if msg_path.exists():
    kesisen = []
    for line in msg_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            d = json.loads(line)
        except Exception:
            continue
        txt = json.dumps(d, ensure_ascii=False)
        if "RAPIDAPI" in txt.upper() and "yasu" in txt.lower():
            kesisen.append(d)
    print(f"RAPIDAPI+yasu iceren kayit: {len(kesisen)}")
    for d in kesisen[-6:]:
        print(json.dumps(d, ensure_ascii=False)[:320])
