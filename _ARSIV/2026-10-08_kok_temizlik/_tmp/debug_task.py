import json
with open('c:/Huginn Data Projesi/Huginn Data Insights/data/orchestrator/task_board.json', 'r', encoding='utf-8') as f:
    tasks = json.load(f)

# Check the exact ID field for one of the review tasks
for t in tasks:
    if 'RAPIDAPI' in t.get('id', '') or 'RAPIDAPI' in t.get('task_id', ''):
        print(f'id: {t.get("id")}')
        print(f'task_id: {t.get("task_id")}')
        print(f'baslik: {t.get("baslik")[:80]}')
        print(f'durum: {t.get("durum")}')
        print('---')