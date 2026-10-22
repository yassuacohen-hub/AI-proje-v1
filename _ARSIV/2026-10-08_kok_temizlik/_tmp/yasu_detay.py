# -*- coding: utf-8 -*-
import json, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
d = json.load(open(r"c:\HUGINN~1\HUGINN~1\data\orchestrator\task_board.json", encoding="utf-8"))
hedef = ("API-V1-NETWORK-REPORT-01", "UI-SSR-NEXT-KUNYE-01",
         "ALTYAPI-REPO-TEMIZLIK-01", "ORCH-KODLAMA-TEMIZLIK-01")
for g in d:
    if g.get("task_id") in hedef:
        print("=" * 60)
        print("ID   :", g.get("task_id"))
        print("baslk:", g.get("baslik"))
        print("drm  :", g.get("durum"), "| oncelik:", g.get("oncelik"), "| sahip:", g.get("sahip"))
        print("brf  :", g.get("brief"))
        print("talmt:", g.get("talimat"))
        print("dosya:", g.get("dosyalar"))
