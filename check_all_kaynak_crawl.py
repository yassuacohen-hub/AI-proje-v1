import json
from pathlib import Path
board_path = Path('Huginn Data Insights/data/orchestrator/task_board.json')
if board_path.exists():
    board = json.loads(board_path.read_text(encoding='utf-8-sig'))
    for t in board:
        tid = t.get('task_id', '')
        if tid.startswith('API-ADMIN-KAYNAK') or tid.startswith('UI-ADMIN-CRAWL'):
            baslik = t.get('baslik', '').replace('\u2192', '->')
            print(tid + " | " + t.get('sahip', '') + " | " + t.get('durum', '') + " | " + t.get('oncelik', '') + " | " + baslik[:80])