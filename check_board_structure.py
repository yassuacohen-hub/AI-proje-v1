from src.company_master.orchestrator import task_board as tb

ids = ["TRIGGER-LOGGING-CLEANUP","ALTYAPI-KILIT-OTOMATIK-01","ALTYAPI-TETIK-ZAMAN-01","ALTYAPI-MOJIBAKE-DIZIN-01","ALTYAPI-MARKA-Huginn-01","ALTYAPI-IMPORT-TEKLES-01"]
print("=== Kanonik pano durumu (task_board.py) ===")
for t in tb.gorev_listesi():
    if t.get("task_id") in ids:
        print(f"{t['task_id']} | durum: {t.get('durum')} | sahip: {t.get('sahip')} | ajan: {t.get('ajan')} | baslik: {t.get('baslik')}")

print("\n=== Onay kuyrugu (son 5) ===")
import json
with open("data/orchestrator/onay_kuyrugu.json", encoding="utf-8") as f:
    revs = json.load(f)
for t in revs[-5:]:
    print(f"{t.get('task_id')} | {t.get('ajan')} | {t.get('durum')}")
