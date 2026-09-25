import json
from pathlib import Path
board_path = Path('Huginn Data Insights/data/orchestrator/task_board.json')
board = json.loads(board_path.read_text(encoding='utf-8-sig'))
for t in board:
    if t.get('task_id') == 'UI-KONTROL-PANOSU-32':
        print('brief:', t.get('brief'))
        print('talimat:', t.get('talimat'))
        break