import json
path = r'C:\Huginn Data Projesi\Huginn Data Insights\data/orchestrator/task_board.json'
with open(path, 'r', encoding='utf-8') as f:
    data = json.load(f)
plan = [t for t in data if t.get('durum') == 'plan']
print('plan tasks:', len(plan))
for t in plan:
    print(f"{t.get('task_id')} | {t.get('baslik')} | sahip={t.get('sahip')} | {t.get('oncelik')}")