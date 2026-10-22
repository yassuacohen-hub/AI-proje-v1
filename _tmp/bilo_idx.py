import json
from pathlib import Path

p = Path(r"c:/Huginn Data Projesi/Huginn Data Insights/data/orchestrator/ajan-chat.jsonl")
sayac = {}
for line in p.read_text(encoding="utf-8").splitlines():
    if not line.strip():
        continue
    s = json.loads(line)
    t = s.get("task_id")
    i = sayac.get(t, 0)
    sayac[t] = i + 1
    if t in ("ALTYAPI-KONG-MULTISITE-01", "ALTYAPI-IP2-8443") and s.get("ajan") == "ihsan":
        print(t, i, s["durum"], "|", s["sorun"][:70])
