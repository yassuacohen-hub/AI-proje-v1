#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Recalc Intelligence Scores - company_intelligence_scores yeniden hesaplar.

Post-scrape workflow Adim 7 olarak calisir.
  ingest_job_postings.py (Adim 5) -> analyze_job_signals.py (Adim 6) -> bu script (Adim 7)

company_signals tablosundaki aktif sinyalleri okur, her sirket icin
ortogonal skorlari (growth, expansion, tech_transformation, investment,
risk, org_change) hesaplar ve company_intelligence_scores tablosuna yazar.

Calistirma:
    python scripts/recalc_intelligence_scores.py [--company-id UUID]
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
LOG_PATH = LOG_DIR / "recalc_intelligence_scores.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_PATH, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger("recalc_intelligence_scores")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="company_intelligence_scores yeniden hesaplama"
    )
    parser.add_argument(
        "--company-id",
        type=str,
        default=None,
        help="Sadece bu şirketi hesapla (UUID). Boş bırakılırsa tüm şirketler.",
    )
    args = parser.parse_args()

    from company_master.intelligence.job_intelligence.pipeline.scorer import (
        score_all_companies,
        score_company,
    )

    log.info("=== Intelligence Score Recalc Başlatılıyor ===")

    try:
        if args.company_id:
            from company_master.db.connection import get_engine
            from sqlalchemy import text
            from uuid import UUID

            engine = get_engine()
            signals_query = text("""
                SELECT signal_id, company_id, signal_type, signal_subtype,
                       score, confidence, evidence, detected_at, valid_until, metadata
                FROM company_signals
                WHERE company_id = :cid
                  AND (valid_until IS NULL OR valid_until > NOW())
            """)
            cid = UUID(args.company_id)
            with engine.connect() as conn:
                rows = conn.execute(signals_query, {"cid": cid}).mappings().all()
            signals = [dict(r) for r in rows]

            if not signals:
                log.warning("Şirket %s için aktif sinyal yok; skor güncellenmedi.", cid)
                print(
                    json.dumps(
                        {
                            "status": "skipped",
                            "company_id": str(cid),
                            "reason": "no signals",
                        },
                        indent=2,
                    )
                )
                return 0

            scores = score_company(cid, signals)
            result = {"status": "ok", "company_id": str(cid), "scores": scores}
            log.info(
                "Şirket %s skorlandı: confidence=%.2f",
                cid,
                scores.get("overall_confidence", 0),
            )
            print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
            return 0

        result = score_all_companies()
        log.info("=== RECALC TAMAMLANDI ===")
        log.info("İşlenen: %d, Atlanan: %d", result["processed"], result["skipped"])

        print(json.dumps(result, indent=2, ensure_ascii=False, default=str))
        return 0

    except Exception as e:
        log.exception("Recalc hatası: %s", e)
        return 1


if __name__ == "__main__":
    sys.exit(main())
