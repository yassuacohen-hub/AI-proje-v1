import json
from pathlib import Path
board_path = Path('Huginn Data Insights/data/orchestrator/task_board.json')
board = json.loads(board_path.read_text(encoding='utf-8-sig'))
for t in board:
    if t.get('sahip') == 'utku' and t.get('durum') == 'bekliyor':
        baslik = t.get('baslik', '').replace('\u2192', '->')
        print(t.get('task_id', '') + " | " + t.get('oncelik', '') + " | " + baslik[:80])