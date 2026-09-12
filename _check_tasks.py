import json
from pathlib import Path
import io

p = Path('data/orchestrator/task_board.json')
b = json.load(io.open(p, encoding='utf-8'))
for t in b:
    if t['task_id'] in ['P7-15','P7-16','P7-17','P7-18','P7-19','P7-20','P7-21']:
        print(t['task_id'], '|', t['durum'], '|', t['baslik'][:60])
