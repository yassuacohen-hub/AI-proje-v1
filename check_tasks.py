import json
from pathlib import Path
board_path = Path('Huginn Data Insights/data/orchestrator/task_board.json')
if board_path.exists():
    board = json.loads(board_path.read_text(encoding='utf-8-sig'))
    for t in board:
        if 'ALTYAPI' in t.get('task_id', ''):
            print(f"{t.get('task_id')}: {t.get('baslik')} | {t.get('sahip')} | {t.get('durum')} | {t.get('oncelik')}")
            print(f"  Dosyalar: {t.get('dosyalar')}")
            print(f"  Brief: {t.get('brief')}")
            print(f"  Talimat: {t.get('talimat')}")
            print()