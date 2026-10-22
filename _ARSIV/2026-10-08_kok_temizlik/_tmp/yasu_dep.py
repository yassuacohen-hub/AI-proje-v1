# -*- coding: utf-8 -*-
import json, sys, os
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
BASE = r"c:\HUGINN~1\HUGINN~1"
d = json.load(open(BASE + r"\data\orchestrator\task_board.json", encoding="utf-8"))
root = d["tasks"] if isinstance(d, dict) and "tasks" in d else d
dep_map = {t.get("task_id"): t.get("durum") for t in root if isinstance(t, dict)}
for dep in ["API-PAKET-SCOPE-01", "API-V1-COMPANY-FRAUD-01", "UI-HUB-4ARTI1-01"]:
    print(f"  {dep}: {dep_map.get(dep, 'KAYIT-YOK')}")
