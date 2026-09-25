import json
from pathlib import Path
board_path = Path('Huginn Data Insights/data/orchestrator/task_board.json')
board = json.loads(board_path.read_text(encoding='utf-8-sig'))
for t in board:
    if 'KVKK-FAQ' in t.get('task_id', ''):
        old_id = t.get('task_id')
        t['task_id'] = 'DOKUMAN-KVKK-FAQ-33'
        t['id'] = 'DOKUMAN-KVKK-FAQ-33'
        print('Fixed task ID: ' + old_id + ' -> ' + t['task_id'])
        break

import sys
sys.path.insert(0, 'Huginn Data Insights/src')
from company_master.orchestrator.task_board import atomic_write_text
atomic_write_text(board_path, json.dumps(board, ensure_ascii=False, indent=2))
print('Updated task board')