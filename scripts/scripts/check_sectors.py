from pathlib import Path
import json

state = json.loads(Path('C:/Projeler/Huginn Data Insights/data/ostim/.scrape_state.json').read_text(encoding='utf-8'))
completed = set(state.get('completed_sectors', {}).keys())
print(f'Completed sectors: {len(completed)}')
for s in sorted(completed):
    page = state['completed_sectors'][s]
    print(f'  {s}: page {page}')