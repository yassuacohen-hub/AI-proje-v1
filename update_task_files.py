import json
from pathlib import Path

board_path = Path('Huginn Data Insights/data/orchestrator/task_board.json')
board = json.loads(board_path.read_text(encoding='utf-8-sig'))

# File paths for the 3 ALTYAPI tasks based on their briefs
task_files = {
    'ALTYAPI-SECRETS-SETUP-01': [
        '.env.example',
        '.env.vault',
        'scripts/rotate_secrets.py',
        'tests/test_secrets_rotation.py',
        'scripts/config_test.py'
    ],
    'ALTYAPI-DB-MIGRATION-01': [
        'scripts/db_migrate.py',
        'src/company_master/schema/migrations/0017_user_activity_log.sql',
        'scripts/db_migrate_prod.sh',
        'backups/'
    ],
    'ALTYAPI-ADMIN-PANO-01': [
        'web_dashboard/tabs/admin_panel.py',
        'tests/test_admin_pano_board_view.py',
        'docs/ADMIN_PANO_BOARD_VIEW.md'
    ]
}

for task in board:
    tid = task.get('task_id')
    if tid in task_files:
        task['dosyalar'] = task_files[tid]
        print(f"Updated {tid} with {len(task_files[tid])} files")

# Write back
import sys
sys.path.insert(0, 'Huginn Data Insights/src')
from company_master.orchestrator.task_board import atomic_write_text
atomic_write_text(board_path, json.dumps(board, ensure_ascii=False, indent=2))
print("Done")