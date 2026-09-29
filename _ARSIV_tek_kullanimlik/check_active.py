import json
with open('data/orchestrator/task_board.json', 'r', encoding='utf-8') as f:
    tasks = json.load(f)
for t in tasks:
    if t.get('sahip') == 'utku' and t.get('durum') not in ['done', 'archive', 'iptal', 'iptal_stale', 'review']:
        print(t['task_id'], '(', t['oncelik'], ') - ', t['durum'], ': ', t['baslik'][:100], sep='')