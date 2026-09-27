import json
with open('data/orchestrator/task_board.json', 'r', encoding='utf-8') as f:
    tasks = json.load(f)
for t in tasks:
    if t['task_id'] == 'VERI-KAYNAK-BAG-01':
        print(f"Status: {t['durum']}")
        print(f"Sahip: {t['sahip']}")
        print(f"Oncelik: {t['oncelik']}")
        print(f"Baslik: {t['baslik']}")
        print(f"Not: {t['not']}")