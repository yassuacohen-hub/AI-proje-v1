import json
from pathlib import Path
board_path = Path('Huginn Data Insights/data/orchestrator/task_board.json')
board = json.loads(board_path.read_text(encoding='utf-8-sig'))
for t in board:
    if t.get('task_id') == 'API-ADMIN-AKTIVITE-YAZ-14':
        print('brief field:', repr(t.get('brief', '')[:200]))
        print('talimat field:', repr(t.get('talimat', '')[:200]))
        break