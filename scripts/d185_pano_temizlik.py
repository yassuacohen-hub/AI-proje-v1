#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""PANO_TUTARSIZLIK_RAPORU_2026-09-21.md aksiyonlarini uygular (idempotent).

- WK-01/02/03: plan -> archive (park edilmis, gercek ajan yok)
- FMT-01, GUARD-ENC-02: blocked -> archive (sahip erteledi, D-48)
- COP-26: blokaj kaldir (COP-25 archive oldu), blocked -> plan
- BRIF-03: blokaj alani bos, blocked nedeni yok -> plan (atanabilir)
"""
import json
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
pano_yolu = root / "data" / "orchestrator" / "task_board.json"

pano = json.loads(pano_yolu.read_text(encoding="utf-8"))

degisti = []

for gorev in pano:
    tid = gorev.get("task_id")

    if tid in ("WK-01", "WK-02", "WK-03") and gorev.get("durum") != "archive":
        gorev["durum"] = "archive"
        degisti.append(tid)

    elif tid in ("FMT-01", "GUARD-ENC-02") and gorev.get("durum") == "blocked":
        gorev["durum"] = "archive"
        gorev["not"] = "Ertelendi (D-48): ADMIN-AYAR-01 onceligi. " + gorev.get("not", "")
        degisti.append(tid)

    elif tid == "COP-26" and gorev.get("durum") == "blocked":
        gorev["blokaj"] = []
        gorev["durum"] = "plan"
        gorev["not"] = "COP-25 archive (basariyla tasindi), blokaj kaldirildi (D-185 temizlik)."
        degisti.append(tid)

    elif tid == "BRIF-03" and gorev.get("durum") == "blocked":
        gorev["durum"] = "plan"
        gorev["not"] = (
            "D-185 temizlik: blokaj alani bos, blocked nedeni bulunamadi -> plan'a cekildi, atanabilir. "
            + gorev.get("not", "")
        )
        degisti.append(tid)

if degisti:
    pano_yolu.write_text(
        json.dumps(pano, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"[OK] Guncellendi: {', '.join(degisti)}")
else:
    print("[ATLA] Guncellenecek gorev bulunamadi (zaten temiz)")

sys.exit(0)
