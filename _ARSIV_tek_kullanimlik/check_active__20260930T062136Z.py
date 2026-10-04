import json
with open('data/orchestrator/task_board.json', 'r', encoding='utf-8') as f:
    tasks = json.load(f)
for t in tasks:
    if t.get('sahip') == 'utku' and t.get('durum') not in ['done', 'archive', 'iptal', 'iptal_stale', 'review']:
        with open('active_tasks.txt', 'a', encoding='utf-8') as out:
            out.write(t['task_id'] + ' (' + t.get('oncelik', '') + ') - ' + t.get('durum', '') + ': ' + t.get('baslik', '')[:100] + '\n')