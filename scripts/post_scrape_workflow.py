#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Post-scrape workflow: ingest detail data, extract VKN from footers, recalculate quality.

Her adim alt process olarak calisir (import izolasyonu + ayri DB baglantisi).
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"

STEPS: list[tuple[str, str]] = [
    ("Adim 1: Detay verilerini DB'ye yaz", "ingest_ostim_detail.py"),
    ("Adim 2: Web footer'dan VKN cikar", "footer_vkn_extractor.py"),
    ("Adim 3: Kalite skorlarini yeniden hesapla", "recalculate_quality_scores.py"),
    ("Adim 4: KPI raporu uret", "generate_kpi_report.py"),
]


def run_step(baslik: str, script: str) -> int:
    print(f"\n=== {baslik} ===")
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS / script)],
        cwd=str(ROOT),
    )
    if proc.returncode != 0:
        print(f"HATA: {script} rc={proc.returncode}")
    return proc.returncode


def main() -> int:
    for baslik, script in STEPS:
        rc = run_step(baslik, script)
        if rc != 0:
            return rc
    print("\n=== Tum adimlar tamamlandi ===")
    # P0-2: Board'daki gorevi done isaretle
    try:
        import sys as _sys
        from pathlib import Path as _Path
        _sys.path.insert(0, str(_Path(__file__).resolve().parents[1] / "src"))
        from company_master.orchestrator import task_board as _tb
        _tb.gorev_guncelle("P0-2", durum="done", **{"not": "Otomatik tetiklendi"})
        _tb.handoff_yaz("P0-2", "Scrape pipeline tamamlandi", "P0-3 kalite kontrol")
    except Exception as exc:
        print(f"[UYARI] Gorev panosu guncellemesi basarisiz: {exc}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
