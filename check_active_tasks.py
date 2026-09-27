import json
with open('data/orchestrator/task_board.json', 'r', encoding='utf-8') as f:
    tasks = json.load(f)
for t in tasks:
    if t.get('sahip') == 'utku' and t.get('durum') in ['aktif', 'plan']:
        print(t['task_id'], t['oncelik'], t['durum'])