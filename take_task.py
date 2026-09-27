import json
from pathlib import Path

board_path = Path('Huginn Data Insights/data/orchestrator/task_board.json')
board = json.loads(board_path.read_text(encoding='utf-8-sig'))

for t in board:
    if t.get('task_id') == 'VERI-NACE-TEMIZ-01':
        t['durum'] = 'aktif'
        t['sahip'] = 'utku'
        print('Updated task status to aktif')
        break

import sys
sys.path.insert(0, 'Huginn Data Insights/src')
from company_master.orchestrator.task_board import atomic_write_text
atomic_write_text(Path('Huginn Data Insights/data/orchestrator/task_board.json'), json.dumps(board, ensure_ascii=False, indent=2))
print('Task status updated to aktif')