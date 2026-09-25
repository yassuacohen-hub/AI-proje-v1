import json
from pathlib import Path
board_path = Path('Huginn Data Insights/data/orchestrator/task_board.json')
board = json.loads(board_path.read_text(encoding='utf-8-sig'))
for t in board:
    if 'KVKK' in t.get('task_id', '') or 'VISIBILITY' in t.get('task_id', '') or 'KONTROL' in t.get('task_id', '') or 'DOKUMAN' in t.get('task_id', ''):
        print(t.get('task_id') + " | " + t.get('durum') + " | " + t.get('oncelik') + " | " + t.get('baslik', '')[:60])