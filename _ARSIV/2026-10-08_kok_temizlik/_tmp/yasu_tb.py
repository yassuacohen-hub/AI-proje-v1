# -*- coding: utf-8 -*-
import json, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
d = json.load(open(r"c:\HUGINN~1\HUGINN~1\data\orchestrator\task_board.json", encoding="utf-8"))
print("ROOT TYPE:", type(d).__name__)
if isinstance(d, dict):
    print("KEYS:", list(d.keys()))
    g = d.get("gorevler") or d.get("tasks") or []
else:
    g = d
try:
    print("TASK COUNT:", len(g))
except Exception:
    print("TASK COUNT: ?")
for t in (g or []):
    tid = str(t.get("id", t.get("task_id", "")))
    if "MUSTERI-ODEME" in tid:
        print("=== BULUNDU ===")
        print(json.dumps(t, ensure_ascii=False, indent=2))
