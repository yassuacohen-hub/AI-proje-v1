# -*- coding: utf-8 -*-
"""utku 3 gorev panodaki durum + son chat mesajlari."""
import json
from pathlib import Path

KOK = Path(r"c:/Huginn Data Projesi/Huginn Data Insights")
pano = json.loads((KOK / "data/orchestrator/task_board.json").read_text(encoding="utf-8"))
for g in pano:
    if g.get("id") in ("MUSTERI-PANEL-TASIMA-T0T2-01", "UX-DUZELT-ROTA-SOZLESMESI-01", "VERI-KAP-HIBRIT-01"):
        print(g["id"], g.get("durum"), g.get("sahip"), g.get("sonuc", "")[:120])
for p in sorted((KOK / "data/orchestrator").glob("chat*.jsonl"))[:3]:
    print("chat dosya:", p.name)
