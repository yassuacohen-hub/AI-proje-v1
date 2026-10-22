# -*- coding: utf-8 -*-
import json, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
d = json.load(open(r"c:\HUGINN~1\HUGINN~1\data\orchestrator\task_board.json", encoding="utf-8"))
HEDEF = [
    "VERI-RAPIDAPI-OSINT-ISTEMCI-01",
    "ALTYAPI-REPO-TEMIZLIK-01",
    "VERI-MUSTERI-ODEME-AYAR-01",
    "ORCH-KODLAMA-TEMIZLIK-01",
    "API-V1-NETWORK-REPORT-01",
    "UI-SSR-NEXT-KUNYE-01",
]
for t in d:
    if t.get("task_id") in HEDEF:
        print("=" * 70)
        print("ID     :", t.get("task_id"))
        print("durum  :", t.get("durum"), "| oncelik:", t.get("oncelik"), "| mod:", t.get("mod"))
        print("baslik :", t.get("baslik"))
        print("brief  :", t.get("brief"))
        print("talimat:", t.get("talimat"))
        print("dosyalar:", t.get("dosyalar"))
        print("deps   :", t.get("dependencies"))
        print("baslangic:", t.get("baslangic"), "| bitis:", t.get("bitis"))

