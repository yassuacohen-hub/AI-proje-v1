import json
from pathlib import Path
board_path = Path('Huginn Data Insights/data/orchestrator/task_board.json')
board = json.loads(board_path.read_text(encoding='utf-8-sig'))
for t in board:
    if t.get('task_id') == 'UI-ADMIN-FEATURE-FLAG-25':
        t['talimat'] = 'UI-ADMIN-FEATURE-FLAG-25: web_dashboard/tabs/admin_panel.py render_feature_flags_tab() + web_app.py POST /api/admin/feature-flags + audit log. Toggle UI, history table, admin only. Test: tests/test_feature_flags.py (3 test).'
        print('Added talimat')
        break

import sys
sys.path.insert(0, 'Huginn Data Insights/src')
from company_master.orchestrator.task_board import atomic_write_text
atomic_write_text(board_path, json.dumps(board, ensure_ascii=False, indent=2))
print('Updated task board')