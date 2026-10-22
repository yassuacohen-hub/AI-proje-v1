# -*- coding: utf-8 -*-
import re
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

t = open(r"c:\HUGINN~1\HUGINN~1\AGENTS.md", encoding="utf-8").read()
L = t.splitlines()
print("SATIR:", len(L))
rx = re.compile(r"teslim|gorev_kutusu|update_task|bitir|rapor_yaz|dogrulama|kapi|gorev yasam|bulgu defteri", re.I)
for i, l in enumerate(L, 1):
    if rx.search(l):
        print(i, l[:130])
