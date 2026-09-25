import json
from pathlib import Path
board_path = Path('Huginn Data Insights/data/orchestrator/task_board.json')
board = json.loads(board_path.read_text(encoding='utf-8-sig'))
for t in board:
    tid = t.get('task_id', '')
    if 'VISIBILITY' in tid or 'KVKK' in tid or 'KONTROL' in tid or 'KVKK-FAQ' in tid or 'DOKUMAN' in tid:
        tid = t.get('task_id', '')
        durum = t.get('durum', '')
        oncelik = t.get('oncelik', '')
        sahip = t.get('sahip', '')
        baslik = t.get('baslik', '').replace('\u2192', '->')
        print(tid + " | " + durum + " | " + oncelik + " | " + sahip + " | " + baslik[:80])