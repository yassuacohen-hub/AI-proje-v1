import json
with open('data/orchestrator/task_board.json', 'r', encoding='utf-8') as f:
    tasks = json.load(f)
for t in tasks:
    if t.get('sahip') == 'utku':
        tid = t.get('task_id', '')
        pri = t.get('oncelik', '')
        dur = t.get('durum', '')
        bas = t.get('baslik', '')[:80]
        with open('all_tasks.txt', 'w', encoding='utf-8') as out:
            out.write(f"{tid} {pri} {dur} {bas}\n")