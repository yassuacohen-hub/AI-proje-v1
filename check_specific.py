import json
from pathlib import Path
board_path = Path('Huginn Data Insights/data/orchestrator/task_board.json')
if board_path.exists():
    board = json.loads(board_path.read_text(encoding='utf-8-sig'))
    for t in board:
        if t.get('sahip') == 'utku':
            tid = t.get('task_id', '')
            if any(x in tid for x in ['KAYNAK', 'CRAWL', 'FEATURE', 'MFA', 'LTV', 'MULTI', 'V9-KUTUCUK']):
                print(tid + " | " + t.get('durum', '') + " | " + t.get('oncelik', '') + " | " + t.get('baslik', '')[:60])