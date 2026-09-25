import json
from pathlib import Path
board_path = Path('Huginn Data Insights/data/orchestrator/task_board.json')
board = json.loads(board_path.read_text(encoding='utf-8-sig'))
for t in board:
    tid = t.get('task_id', '')
    if 'KVKK' in tid or 'RAPOR' in tid or 'RAPOR-28' in tid:
        print(tid + " | " + t.get('durum', '') + " | " + t.get('oncelik', ''))