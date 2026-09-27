import json
with open('data/orchestrator/task_board.json', 'r', encoding='utf-8') as f:
    tasks = json.load(f)
for t in tasks:
    if 'NACE' in t['task_id'] or 'nace' in t['task_id'].lower():
        print(t['task_id'], '(', t['oncelik'], ') - ', t['durum'], ': ', t['baslik'][:80], sep='')