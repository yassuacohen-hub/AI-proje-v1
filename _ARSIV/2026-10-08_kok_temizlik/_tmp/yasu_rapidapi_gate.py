# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
BASE = r"c:\HUGINN~1\HUGINN~1"

print("=== BULGU DEFTERI (RAPIDAPI/OSINT) ===")
d = open(BASE + r"\data\orchestrator\bulgu_defteri.md", encoding="utf-8", errors="replace").read()
for l in d.splitlines():
    if "RAPIDAPI" in l or "OSINT" in l:
        print("  " + l.strip()[:160])

print()
print("=== HUB ADMIN_DASHBOARD basliklar + yasu/RAPIDAPI satirlari ===")
h = open(BASE + r"\hubs\ADMIN_DASHBOARD_HUB.md", encoding="utf-8", errors="replace").read()
lines = h.splitlines()
for i, l in enumerate(lines, 1):
    if l.startswith("#") or "RAPIDAPI" in l or "Kapanan" in l or "MUSTERI-ODEME" in l:
        print(f"  {i}: {l.strip()[:150]}")
