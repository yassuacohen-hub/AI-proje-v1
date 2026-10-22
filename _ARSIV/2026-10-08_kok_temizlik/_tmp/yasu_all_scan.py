# -*- coding: utf-8 -*-
import json, sys
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
TB = r"c:\HUGINN~1\HUGINN~1\data\orchestrator\task_board.json"
d = json.load(open(TB, encoding="utf-8"))
root = d["tasks"] if isinstance(d, dict) and "tasks" in d else d
aktif, done, diger = [], [], []
for t in root:
    if not isinstance(t, dict) or t.get("sahip") != "yasu":
        continue
    durum = t.get("durum", "?")
    tid = t.get("task_id") or t.get("id")
    rec = (durum, tid, t.get("baslik", ""), t.get("bitis"))
    if durum in ("aktif", "devam", "yapiliyor", "pending", "in_progress"):
        aktif.append(rec)
    elif durum in ("done", "tamam", "tamamlandi", "completed"):
        done.append(rec)
    else:
        diger.append(rec)
print(f"=== YASU AKTIF/TESLIM-BEKLEYEN ({len(aktif)}) ===")
for durum, tid, baslik, bitis in sorted(aktif):
    print(f"  [{durum}] {tid}\n        {baslik[:95]}")
print(f"\n=== YASU DIGER ({len(diger)}) ===")
for durum, tid, baslik, bitis in sorted(diger):
    print(f"  [{durum}] {tid} | bitis={bitis}")
print(f"\n=== YASU DONE ({len(done)}) ===")
for durum, tid, baslik, bitis in sorted(done):
    print(f"  {tid}")
