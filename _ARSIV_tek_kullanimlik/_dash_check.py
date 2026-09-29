import json

with open('data/orchestrator/task_board.json', encoding='utf-8') as f:
    d = json.load(f)

with open('_dash_check.txt', 'w', encoding='utf-8') as out:
    for tid in ('DASH-UX-02a', 'DASH-UX-02a-v1', 'ADMIN-UX-MENUTREE-01'):
        found = [t for t in d if t.get('task_id') == tid]
        if not found:
            out.write(f"{tid} => BULUNAMADI\n")
        for t in found:
            out.write(f"{tid} => sahip={t.get('sahip')} durum={t.get('durum')} oncelik={t.get('oncelik')}\n")
