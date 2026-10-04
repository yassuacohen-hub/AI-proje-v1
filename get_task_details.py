import json
with open('data/orchestrator/task_board.json', 'r', encoding='utf-8') as f:
    tasks = json.load(f)
for t in tasks:
    if t['task_id'] == 'VERI-KAYNAK-SIZINTI-01':
        with open('task_details.txt', 'w', encoding='utf-8') as out:
            out.write(f"Baslik: {t.get('baslik', '')}\n")
            out.write(f"Not: {t.get('not', '')}\n")
            out.write(f"Talimat: {t.get('talimat', '')}\n")