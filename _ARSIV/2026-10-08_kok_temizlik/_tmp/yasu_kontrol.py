# -*- coding: utf-8 -*-
import json, io, sys
p = r"c:\HUGINN~1\HUGINN~1\data\orchestrator\task_board.json"
d = json.load(io.open(p, encoding="utf-8"))
targets = ["VERI-MUSTERI-ODEME-AYAR-01", "UI-HUB-4ARTI1-01", "UI-HUB-4ARTI1"]
for t in d:
    tid = str(t.get("task_id", ""))
    if any(x in tid for x in targets):
        print("=== %s ===" % tid)
        for k in ("durum", "oncelik", "sahip", "baslangic", "bitis", "dependencies", "not", "brief"):
            print("  %s: %s" % (k, t.get(k)))
