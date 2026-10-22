import json
import sys
with open('Huginn Data Insights/data/orchestrator/task_board.json', 'r', encoding='utf-8') as f:
    tb = json.load(f)
yasu = [t for t in tb if t.get('sahip') == 'yasu']
print(f"Yasu görevi sayısı: {len(yasu)}", file=sys.stderr)
# Only show non-archive, non-done tasks
active = [t for t in yasu if t['durum'] not in ['archive', 'done']]
print(f"Yasu aktif/goremis sayısı: {len(active)}", file=sys.stderr)
for t in sorted(active, key=lambda x: (x.get('oncelik','Z'), x['task_id'])):
    tid = t['task_id']
    pri = t.get('oncelik', '')
    dur = t['durum']
    bas = t['baslik']
    print(f"  {tid:30s} | {pri:3s} | {dur:8s} | {bas}", file=sys.stderr)