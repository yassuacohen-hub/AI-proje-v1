# -*- coding: utf-8 -*-
"""ajan-chat.jsonl: merge isaretcilerini sil, iki tarafi tut (append-only). Gecersiz JSON satiri sayar."""
import json
import sys
from pathlib import Path

p = Path(sys.argv[1])
satirlar = p.read_text(encoding="utf-8").splitlines()
cikti, atilan, bozuk = [], 0, 0
for s in satirlar:
    if s.startswith(("<<<<<<< ", ">>>>>>> ")) or s == "=======":
        atilan += 1
        continue
    if s.strip():
        try:
            json.loads(s)
        except Exception:
            bozuk += 1
    cikti.append(s)
print(f"giris={len(satirlar)} cikti={len(cikti)} isaretci={atilan} bozuk_json={bozuk}")
if "--yaz" in sys.argv:
    p.write_text("\n".join(cikti) + "\n", encoding="utf-8", newline="\n")
    print("yazildi")
