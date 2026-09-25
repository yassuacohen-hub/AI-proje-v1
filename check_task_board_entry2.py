import json
from pathlib import Path
board_path = Path('Huginn Data Insights/data/orchestrator/task_board.json')
if board_path.exists():
    board = json.loads(board_path.read_text(encoding='utf-8-sig'))
    for t in board:
        if t.get('task_id') == 'DOC-ADMIN-V9-KUTUCUK-24':
            # Replace arrow char
            task_copy = dict(t)
            if 'baslik' in task_copy:
                task_copy['baslik'] = task_copy['baslik'].replace('\u2192', '->')
            if 'brief' in task_copy:
                task_copy['brief'] = task_copy['brief'].replace('\u2192', '->')
            if 'talimat' in task_copy:
                task_copy['talimat'] = task_copy['talimat'].replace('\u2192', '->')
            print(json.dumps(task_copy, ensure_ascii=False, indent=2))
            break