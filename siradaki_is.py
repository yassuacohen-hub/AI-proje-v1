import json
from pathlib import Path

ic = Path(r"c:\Huginn Data Projesi\Huginn Data Insights")
pano = ic / "data" / "orchestrator" / "task_board.json"
gorevler = json.loads(pano.read_text(encoding="utf-8"))

print("=== yasu'ya atanmiş açık görevler (P0/P1 önce) ===")
sira = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
acik = [g for g in gorevler
        if g.get("sahip") == "yasu" 
        and g.get("durum") not in ("done", "archive", "kapandi", "iptal")]
acik.sort(key=lambda g: (sira.get(g.get("oncelik"), 9), g.get("task_id", "")))
for g in acik:
    print(g.get("task_id"), "|", g.get("oncelik"), "|", g.get("durum"), "|", g.get("brief", "")[:60])