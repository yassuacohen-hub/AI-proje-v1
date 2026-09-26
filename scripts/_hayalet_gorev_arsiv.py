#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Hayalet gorevleri arsive tasir (idempotent).

UTKU-02/04/05, ORCH-01..05: dosyalari (src/api/endpoints.py,
src/auth/token_refresh.py, orchestration/*.py, migrations 0020_index_
optimization.sql) kod tabaninda mevcut degil -- kaynak_araştirmasi
sablonundan sizmis placeholder kayitlar. D-57 basligi da uymuyordu.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from src.company_master.orchestrator import task_board as tb  # noqa: E402

HAYALET = ["UTKU-02", "UTKU-04", "UTKU-05", "ORCH-01", "ORCH-02", "ORCH-03", "ORCH-04", "ORCH-05"]
NOT_METNI = "Hayalet gorev (D-XXX): dosya kod tabaninda yok, sablon/placeholder. Arsive tasindi."

degisti = []
for tid in HAYALET:
    g = tb.gorev_getir(tid)
    if g is None:
        print(f"[ATLA] {tid}: panoda yok")
        continue
    if g.get("durum") == "archive":
        print(f"[ATLA] {tid}: zaten archive")
        continue
    tb.gorev_guncelle(tid, durum="archive", **{"not": NOT_METNI + " " + g.get("not", "")})
    degisti.append(tid)

print(f"[OK] Arsive tasindi: {', '.join(degisti) if degisti else '(yok)'}")
