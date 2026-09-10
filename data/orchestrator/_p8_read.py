import json
from pathlib import Path
b = json.loads(Path('data/orchestrator/task_board.json').read_text(encoding='utf-8-sig'))
items = b if isinstance(b, list) else b.get('gorevler', [])
out = []
for g in items:
    gid = str(g.get('id') or g.get('gorev_id') or '')
    if 'P8' in gid.upper() or 'P8' in str(g):
        out.append(json.dumps(g, ensure_ascii=False)[:450])
Path('data/orchestrator/_p8_dump.txt').write_text('\n---\n'.join(out), encoding='utf-8')
print('toplam_gorev:', len(items), '| p8_bulunan:', len(out))
if out:
    print('ornek_alanlar:', list(items[0].keys()))
