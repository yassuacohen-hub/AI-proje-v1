import json
import re
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
K = Path("Huginn Data Insights/data/orchestrator")
for line in (K / "chat" / "messages.jsonl").read_text(encoding="utf-8").splitlines():
    m = json.loads(line)
    if m.get("kimden") == "bilo" and "WEB-SSR-API-ANAHTAR-01" in line and (m.get("ts") or m.get("zaman") or "") >= "2026-10-16":
        print(m.get("ts") or m.get("zaman"), "|", m.get("mesaj"))
# sizinti: ent_ + 9+ karakter (ilk 8'den uzun) son 3 commit diff'inde
diff = subprocess.run(["git", "-C", "Huginn Data Insights", "log", "-p", "-3", "origin/chore/monorepo-merge"],
                      capture_output=True, text=True, encoding="utf-8", errors="replace").stdout
print("SIZINTI:", sorted(set(re.findall(r"ent_[A-Za-z0-9]{12,}", diff))) or "YOK")
html = Path("_tmp/b32_sayfa.html").read_text(encoding="utf-8", errors="replace")
print("ROBOLINK sayfada:", "ROBOL" in html.upper(), "| 404 izi:", "404" in html[:3000])
