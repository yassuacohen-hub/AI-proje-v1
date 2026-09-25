import json
from pathlib import Path

board_path = Path('Huginn Data Insights/data/orchestrator/task_board.json')
board = json.loads(board_path.read_text(encoding='utf-8-sig'))

for task in board:
    if task.get('task_id') == 'DOC-ADMIN-V9-KUTUCUK-24':
        # Set brief to file path, not content
        task['brief'] = 'plans/brief_utku_DOC-ADMIN-V9-KUTUCUK-24.md'
        break

import sys
sys.path.insert(0, 'Huginn Data Insights/src')
from company_master.orchestrator.task_board import atomic_write_text
atomic_write_text(board_path, json.dumps(board, ensure_ascii=False, indent=2))
print("Fixed brief field to file path")