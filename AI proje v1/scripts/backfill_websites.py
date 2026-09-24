#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""source_records.raw_website -> companies.website_domain backfill."""
from __future__ import annotations

import sys
import json
import logging
from pathlib import Path

sys.path.insert(0, "src")
from sqlalchemy import text
from company_master.db.connection import get_engine

ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_PATH = LOG_DIR / "backfill_websites.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(LOG_PATH, encoding="utf-8"), logging.StreamHandler()],
)
log = logging.getLogger("backfill_websites")

BATCH_SIZE = 100


def main() -> int:
    engine = get_engine()

    with engine.connect() as conn:
        # Find companies with NULL website_domain but raw_website exists
        rows = conn.execute(text("""
            SELECT c.company_id, c.legal_name, sr.raw_website
            FROM companies c
            JOIN source_records sr ON sr.source_record_id = c.source_record_id
            WHERE (c.website_domain IS NULL OR c.website_domain = '')
            AND sr.raw_website IS NOT NULL
            AND TRIM(sr.raw_website) != ''
            ORDER BY c.company_id
        """)).mappings().all()

        total = len(rows)
        log.info("Backfill edilecek kayit: %d", total)

        if total == 0:
            print("Backfill edilecek kayit yok.")
            return 0

        processed = 0
        errors = 0
        batch = []

        for row in rows:
            try:
                company_id = row["company_id"]
                raw_website = row["raw_website"].strip()

                # Basic URL normalization
                if raw_website and not raw_website.startswith(("http://", "https://")):
                    raw_website = "https://" + raw_website

                batch.append({"cid": company_id, "web": raw_website})

                if len(batch) >= BATCH_SIZE:
                    conn.execute(text("""
                        UPDATE companies
                        SET website_domain = :web, updated_at = NOW()
                        WHERE company_id = :cid
                    """), batch)
                    conn.commit()
                    processed += len(batch)
                    log.info("Islenen: %d/%d", processed, total)
                    batch = []

            except Exception as e:
                errors += 1
                log.error("Hata (%s): %s", company_id, e)
                try:
                    conn.rollback()
                except Exception:
                    pass
                batch = []

        # Process remaining batch
        if batch:
            try:
                conn.execute(text("""
                    UPDATE companies
                    SET website_domain = :web, updated_at = NOW()
                    WHERE company_id = :cid
                """), batch)
                conn.commit()
                processed += len(batch)
            except Exception as e:
                errors += len(batch)
                log.error("Son batch hatasi: %s", e)
                try:
                    conn.rollback()
                except Exception:
                    pass

        log.info("TAMAM! Islenen: %d, Hata: %d, Toplam: %d", processed, errors, total)
        print(f"Islenen: {processed}, Hata: {errors}, Toplam: {total}")

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
