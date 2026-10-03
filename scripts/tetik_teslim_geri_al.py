# -*- coding: utf-8 -*-
"""Reddedilmiş görevin tetik kaydını `teslim` → `alindi` çeker.

Kullanım: python scripts/tetik_teslim_geri_al.py <ajan> <task_id> "<neden>"
reddet() düzeltmesinden ÖNCE reddedilen kayıtlar için tek seferlik onarım.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, "src")
from company_master.orchestrator import trigger  # noqa: E402


def main(argv: list[str]) -> int:
    if len(argv) != 4:
        print(__doc__)
        return 2
    ajan, task_id, neden = argv[1], argv[2], argv[3]
    kayitlar = trigger._tetikleri_oku(ajan, None)
    n = 0
    for k in kayitlar:
        if k["task_id"] == task_id and k["durum"] == "teslim":
            k["durum"] = "alindi"
            k["red_tarihi"] = trigger._simdi()
            k["red_nedeni"] = neden
            n += 1
    if n:
        trigger._tetikleri_yaz(kayitlar, ajan, None)
    print(f"{task_id}: {n} tetik kaydi teslim->alindi")
    return 0 if n else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
