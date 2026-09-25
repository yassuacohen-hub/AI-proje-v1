import json
from pathlib import Path
board_path = Path('Huginn Data Insights/data/orchestrator/task_board.json')
if board_path.exists():
    board = json.loads(board_path.read_text(encoding='utf-8-sig'))
    for t in board:
        if t.get('task_id') == 'DOC-ADMIN-V9-KUTUCUK-24':
            print(json.dumps(t, ensure_ascii=False, indent=2))
            break