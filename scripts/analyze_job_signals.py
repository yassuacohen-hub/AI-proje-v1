#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Job Signals Analyzer - job_postings'ten company_signals üretir.

Post-scrape workflow Adim 6 olarak calisir.
  ingest_job_postings.py (Adim 5) -> bu script (Adim 6) -> recalc_intelligence_scores.py (Adim 7)

Calistirma:
    python scripts/analyze_job_signals.py [--window-days 90]

DB'deki son 90 gundeki job_postings kayitlarini okur, her sirket icin
6 sinyal turunu (growth, risk, tech_transformation, investment,
geo_expansion, org_change) tespit eder ve company_signals tablosuna yazar.
"""

from __future__ import annotations
import argparse
import json
import logging
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_PATH = LOG_DIR / "analyze_job_signals.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_PATH, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("analyze_job_signals")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Job postings -> company_signals analiz motoru"
    )
    parser.add_argument(
        "--window-days",
        type=int,
        default=90,
        help="Analiz penceresi (gün). Varsayılan: 90",
    )
    args = parser.parse_args()

    from company_master.intelligence.job_intelligence.pipeline.analyzer import (
        SignalAnalyzer,
    )

    log.info("=== Signal Analyzer Başlatılıyor (window=%d gün) ===", args.window_days)

    try:
        analyzer = SignalAnalyzer(window_days=args.window_days)
        result = analyzer.analyze()

        log.info("=== ANALİZ TAMAMLANDI ===")
        log.info("İşlenen şirket: %d", result["companies_processed"])
        log.info("Üretilen sinyal: %d", result["signals_generated"])
        for sig_type, count in sorted(result["by_type"].items()):
            log.info("  %s: %d", sig_type, count)

        print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
        return 0

    except Exception as e:
        log.exception("Signal analyzer hatası: %s", e)
        return 1


if __name__ == "__main__":
    sys.exit(main())
