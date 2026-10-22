# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
BASE = r"c:\HUGINN~1\HUGINN~1"
sys.path.insert(0, BASE)
sys.path.insert(0, BASE + r"\src")

from src.company_master.orchestrator import task_board as tb

liste = tb.gorev_listesi()
print(f"TOPLAM gorev: {len(liste)}\n")

# yasu gorevlerini durumuna gore grupla
from collections import defaultdict
grup = defaultdict(list)
for g in liste:
    sahip = g.get("sahip")
    if sahip == "yasu":
        grup[g.get("durum")].append(g.get("task_id"))

for durum in sorted(grup):
    print(f"== {durum} ({len(grup[durum])}) ==")
    for t in grup[durum]:
        print(f"   {t}")
    print()

# RAPIDAPI ozel durum
r = tb.gorev_getir("VERI-RAPIDAPI-OSINT-ISTEMCI-01")
if r:
    print("=== RAPIDAPI anlik durum ===")
    print("  durum:", r.get("durum"))
    print("  sahip:", r.get("sahip"))
    print("  bitis:", r.get("bitis"))



