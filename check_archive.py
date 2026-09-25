import json
from pathlib import Path
archive_path = Path('Huginn Data Insights/data/orchestrator/task_board_arsiv_2026-Q3.json')
if archive_path.exists():
    archive = json.loads(archive_path.read_text(encoding='utf-8-sig'))
    for t in archive:
        tid = t.get('task_id', '')
        if any(x in tid for x in ['SAHTE', 'KULLANICI', 'GUNCELLIK', 'MALIYET', 'ARSIV-12']):
            print(f"{tid}: {t.get('baslik')} | {t.get('durum')}")