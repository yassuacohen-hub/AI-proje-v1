import json
from pathlib import Path
board_path = Path('Huginn Data Insights/data/orchestrator/task_board.json')
if board_path.exists():
    board = json.loads(board_path.read_text(encoding='utf-8-sig'))
    for t in board:
        tid = t.get('task_id', '')
        sahip = t.get('sahip', '')
        durum = t.get('durum', '')
        if durum in ('bekliyor', 'yedek') and sahip != 'utku':
            baslik = t.get('baslik', '').replace('\u2192', '->')
            print(tid + " | " + sahip + " | " + durum + " | " + t.get('oncelik', '') + " | " + baslik[:80])