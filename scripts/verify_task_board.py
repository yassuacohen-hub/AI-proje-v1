"""Pano tutarlılık doğrulama (adli inceleme son adımı)."""
import hashlib
import json
import os
import time
from collections import Counter

P = "data/orchestrator/task_board.json"

b = json.loads(open(P, encoding="utf-8-sig").read())
print("PANO_MTIME:", time.ctime(os.path.getmtime(P)))
print("PANO_HASH:", hashlib.sha256(open(P, "rb").read()).hexdigest()[:16])
print("GOREV_SAYISI:", len(b))

ids = [t["task_id"] for t in b]
c = Counter(ids)
dups = [k for k, v in c.items() if v > 1]
print("DUPLIKE_ID:", dups if dups else "YOK")

aktif = [t for t in b if t["durum"] not in ("done",)]
print("AKTIF_PLAN:", [(t["task_id"], t["durum"]) for t in aktif])

r9 = [t for t in b if t["task_id"] == "9R-01"]
print("9R-01:", [(t["task_id"], t["durum"], t["bitis"]) for t in r9])

md = open("data/orchestrator/gorev_panosu.md", encoding="utf-8").read()
sync = open("AGENT_SYNC.md", encoding="utf-8").read()
print("PANODA_DUPLICATE_TEST:", any(t["task_id"] == "DUPLICATE-TEST" for t in b))
print("MD_ICERIR_DUPLICATE_TEST:", "DUPLICATE-TEST" in md)
print("SYNC_SON_GUNCELLEME:", [l for l in sync.splitlines() if "Son guncelleme" in l or "son guncelleme" in l])

# dosya kilidi dosya-check: kilitli her dosya panoda gorunuyor mu
fl = json.loads(open("data/orchestrator/file_locks.json", encoding="utf-8-sig").read())
lock_task_ids = [v.get("task_id") for v in fl.values() if isinstance(v, dict)]
board_ids = set(ids)
bilinmeyen = sorted(set(lock_task_ids) - board_ids)
print("KILIT_SAHIPLERI_PANODA_OLMAYAN:", bilinmeyen if bilinmeyen else "YOK")
print("KILIT_SAYISI:", len(fl))