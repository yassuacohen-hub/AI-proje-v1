# -*- coding: utf-8 -*-
"""RAPIDAPI acik kayitlarini index ile listele + kapatma kontrolu."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(r"c:\HUGINN~1\HUGINN~1\src")))
from company_master import chat

TASK = "VERI-RAPIDAPI-OSINT-ISTEMCI-01"
satirlar = chat.oku(task_id=TASK)
print(f"=== {TASK}: {len(satirlar)} kayit ===")
for i, s in enumerate(satirlar):
    if s.get("durum") == "acik":
        print(f"[{i}] ACIK  kimden={s.get('kimden')} | {s.get('sorun','')[:90]}")

print()
k = chat.teslim_kontrol_et(TASK)
print(f"teslim_kontrol_et: engel={k['engel']} neden={len(k['nedenler'])}")
for n in k["nedenler"]:
    print(f"  - {n[:100]}")
