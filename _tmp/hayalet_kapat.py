import json
P = "Huginn Data Insights/data/orchestrator/task_board.json"
d = json.load(open(P, encoding="utf-8"))
tasks = d["tasks"] if isinstance(d, dict) else d
notlar = {
    "FE-REACT-FLOW-ŞIRKET-ILIŞKILERI-A-008": "KALICI KAPALI (ihsan 2026-10-16): yerine UI-NETWORK-GRAF-01 (yasu) acildi — network_router.py:89-95 kenarlar yalniz parent->child, derinlik<=2 => agac, React Flow gereksiz (D-211 ikiz yasagi).",
    "FE-TREMOR-RAW-GRAFIK-BILEŞENLERI-010": "KALICI KAPALI (ihsan 2026-10-16): kapsam UI-TICARIRADAR-PANEL-01 Faz A icinde (brief:20-21 'Tremor Raw KPI kartlari'); ayri gorev = kopya.",
    "API-ESCROW-DIJITAL-TAHKIM-API-011": "KALICI KAPALI (ihsan 2026-10-16): STRATEJI_08:102-103 iyzico pazar yeri/escrow BIRINCIL saglayici, S07 checkout tasarimina bagli; odeme saglayici entegrasyonu olmadan tahkim API yazilamaz. S07 checkout kapaninca PO onayiyla yeni brif.",
}
n = 0
for t in tasks:
    tid = t.get("task_id")
    if tid in notlar:
        t["not"] = notlar[tid] + " | " + t.get("not", "")
        t["durum"] = "archive"
        n += 1
assert n == 3, n
json.dump(d, open(P, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
open(P, "a", encoding="utf-8").write("\n")
print("guncellendi", n)
