import json
from pathlib import Path
archive_path = Path('Huginn Data Insights/data/orchestrator/task_board_arsiv_2026-Q3.json')
if archive_path.exists():
    archive = json.loads(archive_path.read_text(encoding='utf-8-sig'))
    targets = ['UI-ADMIN-SAHTE-KPI-01', 'UI-ADMIN-SAHTE-EXEC-02', 'UI-ADMIN-KULLANICI-BIRLESTIR-09', 'UI-ADMIN-GUNCELLIK-KOVA-10', 'UI-ADMIN-MALIYET-ANOMALI-11', 'DOC-ADMIN-ARSIV-12']
    for t in archive:
        if t.get('task_id') in targets:
            print(t.get('task_id') + ": " + t.get('durum', 'N/A'))