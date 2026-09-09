#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""NULL source_record_id kayitlarini source_records'a bagla."""
from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from sqlalchemy import text
from company_master.db.connection import get_engine

ROOT = Path(__file__).resolve().parents[1]
LOG_DIR = ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_PATH = LOG_DIR / "fix_null_source_records.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler(LOG_PATH, encoding="utf-8"), logging.StreamHandler()],
)
log = logging.getLogger("fix_null_source_records")


def main() -> int:
    engine = get_engine()
    
    with engine.begin() as conn:
        # NULL source_record_id olan firmalari bul
        rows = conn.execute(text("""
            SELECT c.company_id, c.legal_name, c.tax_number, c.primary_phone, 
                   c.primary_email, c.website_domain, c.osb_id, c.is_osb_member
            FROM companies c
            WHERE c.source_record_id IS NULL
            ORDER BY c.company_id
        """)).mappings().all()
        
        total = len(rows)
        log.info("NULL source_record_id olan %d firma bulundu", total)
        
        if total == 0:
            print("Hic NULL source_record_id kaydi yok.")
            return 0
        
        processed = 0
        errors = 0
        
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
                
                # Kaynak belirleme
                if is_osb_member:
                    source_name = "ostim.org.tr"
                elif osb_id:
                    source_name = str(osb_id)
                else:
                    source_name = "manual"
                
                # Source record olustur
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
                
                # Company'yi guncelle
                conn.execute(text("""
                    UPDATE companies 
                    SET source_record_id = :sid, updated_at = NOW()
                    WHERE company_id = :cid
                """), {"sid": source_record_id, "cid": company_id})
                
                processed += 1
                
                if processed % 100 == 0:
                    log.info("Islenen: %d/%d", processed, total)
                    
            except Exception as e:
                errors += 1
                log.error("Hata (%s): %s", company_id, e)
        
        log.info("TAMAM! Islenen: %d, Hata: %d, Toplam: %d", processed, errors, total)
        print(f"Islenen: {processed}, Hata: {errors}, Toplam: {total}")
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
