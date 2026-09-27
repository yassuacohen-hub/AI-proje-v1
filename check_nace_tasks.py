import json
from pathlib import Path

board_path = Path('Huginn Data Insights/data/orchestrator/task_board.json')
board = json.loads(board_path.read_text(encoding='utf-8-sig'))

for t in board:
    if 'NACE' in t.get('task_id', '') or 'SOZLUK' in t.get('task_id', '') or 'KOLON' in t.get('task_id', ''):
        tid = t.get('task_id', '')
        durum = t.get('durum', '')
        oncelik = t.get('oncelik', '')
        baslik = t.get('baslik', '').replace('\u2192', '->')
        print(tid + ' | ' + durum + ' | ' + oncelik + ' | ' + baslik[:80])