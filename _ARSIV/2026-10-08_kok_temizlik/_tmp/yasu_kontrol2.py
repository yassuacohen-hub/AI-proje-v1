# -*- coding: utf-8 -*-
import json
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

TB = r"c:\HUGINN~1\HUGINN~1\data\orchestrator\task_board.json"
d = json.load(open(TB, encoding="utf-8"))
tasks = d.get("tasks", []) if isinstance(d, dict) else d

hedef = [
    "ALTYAPI-REPO-TEMIZLIK-01",
    "API-V1-NETWORK-REPORT-01",
    "UI-SSR-NEXT-KUNYE-01",
    "ORCH-KODLAMA-TEMIZLIK-01",
    "VERI-RAPIDAPI-OSINT-ISTEMCI-01",
]
for t in tasks:
    tid = t.get("task_id") or t.get("id")
    if tid in hedef:
        print("=" * 70)
        print(f"TASK: {tid}  durum={t.get('durum')} oncelik={t.get('oncelik')}")
        print(f"BASLIK: {t.get('baslik')}")
        print(f"BASLANGIC: {t.get('baslangic')}  BITIS: {t.get('bitis')}")
        print(f"BRIEF: {t.get('brief')}")
        print(f"DOSYALAR: {t.get('dosyalar')}")
        print(f"TALIMAT: {t.get('talimat')}")
        print(f"NOT: {t.get('not')}")
        print()





