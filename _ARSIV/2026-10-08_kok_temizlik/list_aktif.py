import json
d=json.load(open('Huginn Data Insights/data/orchestrator/task_board.json','r',encoding='utf-8'))
for t in d:
    if t.get('durum') == 'aktif':
        print(f"{t.get('task_id')} | {t.get('sahip')} | {t.get('oncelik')} | {t.get('baslik', '')[:80]}")