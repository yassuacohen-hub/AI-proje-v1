import json
from pathlib import Path
board_path = Path('Huginn Data Insights/data/orchestrator/task_board.json')
board = json.loads(board_path.read_text(encoding='utf-8-sig'))
for t in board:
    if 'KVKK-FAQ' in t.get('task_id', ''):
        # Replace arrow chars
        t_clean = dict(t)
        if 'baslik' in t_clean:
            t_clean['baslik'] = t_clean['baslik'].replace('\u2192', '->')
        if 'brief' in t_clean:
            t_clean['brief'] = t_clean['brief'].replace('\u2192', '->')
        if 'talimat' in t_clean:
            t_clean['talimat'] = t_clean['talimat'].replace('\u2192', '->')
        with open('faq_task.json', 'w', encoding='utf-8') as f:
            json.dump(t_clean, f, ensure_ascii=False, indent=2)
        print('Written to faq_task.json')
        break