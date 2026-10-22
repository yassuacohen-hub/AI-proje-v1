# -*- coding: utf-8 -*-
import re
import sys
import pathlib
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
BASE = pathlib.Path(r"c:\HUGINN~1\HUGINN~1")

# 1) gorev_kutusu.py icinde hafiza kapisi mantigini cikar
src = (BASE / "scripts" / "gorev_kutusu.py").read_text(encoding="utf-8", errors="replace").splitlines()
print("=== gorev_kutusu.py hafiza/hub satirlari ===")
for i, l in enumerate(src):
    if re.search(r"def _hafiza|hub_b14|hubs/|_HUB|PLAN_STRATEGY|ADMIN_DASHBOARD", l):
        print(f"{i+1}: {l}")

print("\n=== PLAN_STRATEGY_HUB.md basliklari ===")
p = BASE / "hubs" / "PLAN_STRATEGY_HUB.md"
if p.exists():
    for i, l in enumerate(p.read_text(encoding="utf-8", errors="replace").splitlines()):
        if re.match(r"^#+ ", l):
            print(f"  {i+1}: {l}")
else:
    print("  (DOSYA YOK)")
