import json
with open('data/orchestrator/task_board.json', encoding='utf-8') as f:
    data = json.load(f)
tasks = data[0]['tasks']
print('=== ALTYAPI Tasks ===')
for t in tasks:
    tid = t.get('id', '')
    if tid.startswith('ALTYAPI-KILIT') or tid.startswith('ALTYAPI-TETIK') or tid.startswith('ALTYAPI-MOJIBAKE') or tid.startswith('TRIGGER'):
        print(f"{tid} | {t.get('assigned_to','')} | {t.get('priority','')} | {t.get('status','')}")
