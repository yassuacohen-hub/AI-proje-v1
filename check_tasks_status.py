import json
p = "data/orchestrator/task_board.json"
d = json.load(open(p, encoding="utf-8"))
ids = ["ALTYAPI-KILIT-OTOMATIK-01","ALTYAPI-TETIK-ZAMAN-01","ALTYAPI-MOJIBAKE-DIZIN-01","TRIGGER-LOGGING-CLEANUP","ALTYAPI-MARKA-HUGGINN-01","ALTYAPI-IMPORT-TEKLES-01"]
for t in d:
    if t.get("task_id") in ids:
        print(f"{t['task_id']} | durum: {t.get('durum','?')} | sahip: {t.get('sahip','?')} | ajan: {t.get('ajan','?')}")
