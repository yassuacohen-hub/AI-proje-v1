import json
from pathlib import Path

board_path = Path('Huginn Data Insights/data/orchestrator/task_board.json')
board = json.loads(board_path.read_text(encoding='utf-8-sig'))

# Task IDs that are already archived and should be removed from current board
archived_ids = [
    'UI-ADMIN-SAHTE-KPI-01',
    'UI-ADMIN-SAHTE-EXEC-02', 
    'UI-ADMIN-KULLANICI-BIRLESTIR-09',
    'UI-ADMIN-GUNCELLIK-KOVA-10',
    'UI-ADMIN-MALIYET-ANOMALI-11',
    'DOC-ADMIN-ARSIV-12'
]

# Filter out archived tasks
new_board = [t for t in board if t.get('task_id') not in archived_ids]

print(f"Removed {len(board) - len(new_board)} archived tasks")
print(f"Board now has {len(new_board)} tasks")

# Write back
import sys
sys.path.insert(0, 'Huginn Data Insights/src')
from company_master.orchestrator.task_board import atomic_write_text
atomic_write_text(board_path, json.dumps(new_board, ensure_ascii=False, indent=2))
print("Done")