import json
from pathlib import Path
board_path = Path('Huginn Data Insights/data/orchestrator/task_board.json')
board = json.loads(board_path.read_text(encoding='utf-8-sig'))
for t in board:
    if t.get('task_id') == 'DOC-VISIBILITY-KATMANI-29':
        t['brief'] = 'Huginn Data Insights/plans/brief_utku_DOC-VISIBILITY-KATMANI-29.md'
        print('Fixed brief path to absolute from project root')
        break

import sys
sys.path.insert(0, 'Huginn Data Insights/src')
from company_master.orchestrator.task_board import atomic_write_text
atomic_write_text(board_path, json.dumps(board, ensure_ascii=False, indent=2))
print('Updated task board')