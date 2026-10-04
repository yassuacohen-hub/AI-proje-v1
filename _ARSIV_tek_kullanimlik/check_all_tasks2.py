import json
with open('data/orchestrator/task_board.json', 'r', encoding='utf-8') as f:
    tasks = json.load(f)

utku_tasks = [t for t in tasks if t.get('sahip') == 'utku']

with open('all_tasks.txt', 'w', encoding='utf-8') as out:
    for t in utku_tasks:
        tid = t.get('task_id', '')
        pri = t.get('oncelik', '')
        dur = t.get('durum', '')
        bas = t.get('baslik', '')[:80]
        out.write(f"{tid} {pri} {dur} {bas}\n")