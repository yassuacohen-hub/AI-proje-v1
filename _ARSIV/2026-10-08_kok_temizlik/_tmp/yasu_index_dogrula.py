# -*- coding: utf-8 -*-
import sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.path.insert(0, "src")
from company_master import chat

tid = "VERI-RAPIDAPI-OSINT-ISTEMCI-01"
p = chat._log_path()
satirlar = [__import__("json").loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]
idx = 0
for s in satirlar:
    if s.get("task_id") == tid.upper():
        print(f"index={idx} | durum={s.get('durum')} | kimden={s.get('kimden')}")
        print(f"   sorun: {str(s.get('sorun'))[:140]}")
        idx += 1
