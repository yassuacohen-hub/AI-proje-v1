# -*- coding: utf-8 -*-
"""bilo'dan gelen son chat satirlari (kisaltilmis). Sadece okur."""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
P = Path(r"c:\Huginn Data Projesi\Huginn Data Insights\data\orchestrator\chat\messages.jsonl")
satirlar = []
for ln in P.read_text(encoding="utf-8-sig", errors="replace").splitlines():
    try:
        satirlar.append(json.loads(ln))
    except Exception:
        pass
print("toplam:", len(satirlar), "| anahtarlar:", sorted(satirlar[-1].keys()))
for s in satirlar[-40:]:
    kim = str(s.get("kimden") or s.get("from") or "")
    if "bilo" in kim.lower() or "bilo" in str(s.get("kime") or s.get("to") or "").lower():
        m = str(s.get("mesaj") or s.get("text") or s.get("soru") or "").replace("\n", " ")
        print(s.get("ts") or s.get("tarih"), "|", kim, "->", s.get("kime") or s.get("to"), "|", s.get("task_id"), "|", s.get("durum"), "|", m[:260])
