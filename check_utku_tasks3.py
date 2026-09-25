import json
from pathlib import Path
board_path = Path('Huginn Data Insights/data/orchestrator/task_board.json')
if board_path.exists():
    board = json.loads(board_path.read_text(encoding='utf-8-sig'))
    for t in board:
        if t.get('sahip') == 'utku':
            tid = t.get('task_id', '')
            baslik = t.get('baslik', '').replace('\u2192', '->')
            durum = t.get('durum', '')
            oncelik = t.get('oncelik', '')
            print(tid + " | " + durum + " | " + oncelik + " | " + baslik[:50])