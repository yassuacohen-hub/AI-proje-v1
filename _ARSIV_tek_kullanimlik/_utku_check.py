import json

with open('data/orchestrator/task_board.json', encoding='utf-8') as f:
    d = json.load(f)

utku = [t for t in d if t.get('sahip') == 'utku' and t.get('durum') not in ('done', 'iptal')]

with open('_utku_bekleyen.txt', 'w', encoding='utf-8') as f:
    f.write(f"toplam={len(d)} utku_bekleyen={len(utku)}\n")
    for t in utku:
        baslik = (t.get('baslik') or '')[:90]
        f.write(f"{t.get('task_id')} | {t.get('durum')} | {t.get('oncelik')} | {baslik}\n")
