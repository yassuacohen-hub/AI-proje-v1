# -*- coding: utf-8 -*-
import json, sys
sys.stdout.reconfigure(encoding="utf-8")
P = r"c:\Huginn Data Projesi\Huginn Data Insights\data\orchestrator\task_board.json"
g = json.load(open(P, encoding="utf-8"))
from collections import Counter
print("toplam", len(g), Counter(t.get("durum") for t in g))
print("sahip x durum:", Counter((t.get("sahip"), t.get("durum")) for t in g if t.get("durum") not in ("done", "iptal", "arsiv")))
for t in g:
    if t.get("durum") not in ("done", "iptal", "arsiv"):
        print(f'{t.get("durum"):10} {t.get("oncelik","-"):4} {str(t.get("sahip")):8} {t["id"]:45} dep={t.get("dependencies",[])} | {t.get("baslik","")[:70]} | not={str(t.get("not",""))[:80]}')
