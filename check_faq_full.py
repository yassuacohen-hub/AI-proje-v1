import json
from pathlib import Path
board_path = Path('Huginn Data Insights/data/orchestrator/task_board.json')
board = json.loads(board_path.read_text(encoding='utf-8-sig'))
for t in board:
    if 'KVKK-FAQ' in t.get('task_id', ''):
        print(json.dumps(t, ensure_ascii=False, indent=2))
        break