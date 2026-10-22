import json
with open('c:/Huginn Data Projesi/Huginn Data Insights/data/orchestrator/task_board.json', 'r', encoding='utf-8') as f:
    tasks = json.load(f)

review_tasks = [t for t in tasks if t.get('durum') == 'review']
active_tasks = [t for t in tasks if t.get('durum') in ['active', 'in_progress']]

print(f'=== REVIEW ({len(review_tasks)}) ===')
for t in review_tasks:
    print(f"  {t.get('id')}: {t.get('baslik')} | ajan: {t.get('ajan')} | oncelik: {t.get('oncelik')}")

print(f'\n=== ACTIVE/IN_PROGRESS ({len(active_tasks)}) ===')
by_agent = {}
for t in active_tasks:
    a = t.get('ajan', 'none')
    by_agent[a] = by_agent.get(a, 0) + 1
for a, c in sorted(by_agent.items()):
    print(f'  {a}: {c}')
for t in active_tasks:
    print(f"  {t.get('id')}: {t.get('baslik')} | ajan: {t.get('ajan')} | oncelik: {t.get('oncelik')}")