# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import re

p = r"c:\HUGINN~1\HUGINN~1\hubs\ADMIN_DASHBOARD_HUB.md"
L = open(p, encoding="utf-8").read().splitlines()
print("SATIR:", len(L))
# basliklari ve "kapanan" gecen satirlari goster
for i, l in enumerate(L, 1):
    if l.startswith("#") or re.search(r"kapanan|kapanmi|kapanan", l, re.I):
        print(f"{i}: {l[:120]}")
