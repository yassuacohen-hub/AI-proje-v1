import json
from pathlib import Path
board_path = Path('Huginn Data Insights/data/orchestrator/task_board.json')
board = json.loads(board_path.read_text(encoding='utf-8-sig'))
with open('kvkk_status.txt', 'w', encoding='utf-8') as f:
    for t in board:
        if 'KVKK' in t.get('task_id', ''):
            tid = t.get('task_id', '')
            durum = t.get('durum', '')
            oncelik = t.get('oncelik', '')
            baslik = t.get('baslik', '').replace('\u2192', '->')
            f.write(tid + ' | ' + durum + ' | ' + oncelik + ' | ' + baslik[:80] + '\n')
print('Written to kvkk_status.txt')