#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""NULL source_record_id kayitlarini source_records'a bagla veya temizle."""
from __future__ import annotations

import json
import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

from sqlalchemy import text

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from company_master.db.connection import get_engine

LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_PATH = LOG_DIR / "fix_and_clean_null_source_records.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(LOG_PATH, encoding="utf-8"), logging.StreamHandler()],
)
log = logging.getLogger("fix_and_clean_null_source_records")

ORCHESTRATOR_DIR = ROOT / "data" / "orchestrator"
ORCHESTRATOR_DIR.mkdir(parents=True, exist_ok=True)


def main() -> int:
    engine = get_engine()
    result = {
        "task": "p42",
        "ts": datetime.now().isoformat(),
        "null_count": 0,
        "linked_count": 0,
        "cleaned_count": 0,
        "errors": [],
        "status": "ok",
    }

    with engine.begin() as conn:
        rows = conn.execute(text("""
            SELECT c.company_id, c.legal_name, c.tax_number, c.primary_phone,
                   c.primary_email, c.website_domain, c.osb_id, c.is_osb_member
            FROM companies c
            WHERE c.source_record_id IS NULL
            ORDER BY c.company_id
        """)).mappings().all()

        total = len(rows)
        result["null_count"] = total
        log.info("NULL source_record_id olan %d firma bulundu", total)

        if total == 0:
            print("Hic NULL source_record_id kaydi yok.")
            result["status"] = "no_action"
        else:
            for row in rows:
                try:
                    company_id = row["company_id"]
                    legal_name = row["legal_name"] or ""
                    tax_number = row["tax_number"]
                    phone = row["primary_phone"]
                    email = row["primary_email"]
                    website = row["website_domain"]
                    osb_id = row["osb_id"]
                    is_osb_member = row["is_osb_member"]

                    if is_osb_member:
                        source_name = "ostim.org.tr"
                    elif osb_id:
                        source_name = str(osb_id)
                    else:
                        source_name = "manual"

                    payload = {
                        "legal_name": legal_name,
                        "fix_type": "null_source_record_id_fix",
                        "fixed_at": datetime.now().isoformat(),
                    }

                    sr_result = conn.execute(text("""
                        INSERT INTO source_records
                        (source_id, external_id, raw_name, raw_phone, raw_email,
                         raw_website, raw_tax_number, raw_payload, collected_at)
                        VALUES (
                            (SELECT source_id FROM sources WHERE source_name = :sname LIMIT 1),
                            :ext_id,
                            :name,
                            :phone,
                            :email,
                            :website,
                            :tax,
                            CAST(:payload AS jsonb),
                            NOW()
                        )
                        RETURNING source_record_id
                    """), {
                        "sname": source_name,
                        "ext_id": f"fix_{company_id}",
                        "name": legal_name,
                        "phone": phone,
                        "email": email,
                        "website": website,
                        "tax": tax_number,
                        "payload": json.dumps(payload, ensure_ascii=False),
                    })

                    source_record_id = sr_result.first()[0]

                    if source_record_id is None:
                        raise ValueError(f"Kaynak bulunamadi: {source_name}")

                    conn.execute(text("""
                        UPDATE companies
                        SET source_record_id = :sid, updated_at = NOW()
                        WHERE company_id = :cid
                    """), {"sid": source_record_id, "cid": company_id})

                    result["linked_count"] += 1

                except Exception as e:
                    try:
                        conn.execute(text("""
                            DELETE FROM companies WHERE company_id = :cid
                        """), {"cid": row["company_id"]})
                        result["cleaned_count"] += 1
                        log.info("Temizlendi (kaynak yok): %s - %s", row["company_id"], e)
                    except Exception as del_err:
                        result["errors"].append(
                            f"{row['company_id']}: baglanti hatasi={e}, temizleme hatasi={del_err}"
                        )
                        log.error("Hata (%s): %s", row["company_id"], e)

            log.info(
                "TAMAM! NULL: %d, Baglanan: %d, Temizlenen: %d, Hata: %d",
                total,
                result["linked_count"],
                result["cleaned_count"],
                len(result["errors"]),
            )
            print(
                f"NULL: {total}, Baglanan: {result['linked_count']}, "
                f"Temizlenen: {result['cleaned_count']}, Hata: {len(result['errors'])}"
            )

    result_path = ORCHESTRATOR_DIR / "p42_result.json"
    result_path.write_text(
        json.dumps(result, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    log.info("Sonuc kaydedildi: %s", result_path)
    print(f"Sonuc kaydedildi: {result_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
