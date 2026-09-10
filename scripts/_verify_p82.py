import json
from pathlib import Path
board = json.loads(Path("C:\Projeler\Huginn Data Insights\data\orchestrator\task_board.json").read_text(encoding="utf-8"))
for t in board:
    tid = t.get("task_id") or t.get("id")
    if tid == "P8-2":
        print(f"task_id={t.get('task_id')} id={t.get('id')} durum={t['durum']} bitis={t.get('bitis')}")
        break
