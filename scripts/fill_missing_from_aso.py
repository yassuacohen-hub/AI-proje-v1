#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""ASO verisinden adres ve email eksiklerini doldur."""
import json, sys
from pathlib import Path
from sqlalchemy import text

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from company_master.db.connection import get_engine

ASO_PATH = ROOT / "data" / "aso" / "aso_full.jsonl"
engine = get_engine()

# Load ASO data
records = []
with open(ASO_PATH, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if line:
            try:
                records.append(json.loads(line))
            except:
                pass

print(f"ASO kaydı: {len(records)}")

# Build lookup by cleaned company name
aso_lookup = {}
for rec in records:
    raw_unvan = (rec.get("unvan") or "").strip()
    prefix = "(İFLAS NEDENİYLE) TASFİYE HALİNDE "
    unvan = raw_unvan[len(prefix):].strip() if raw_unvan.startswith(prefix) else raw_unvan
    aso_lookup[unvan.lower()] = rec

with engine.connect() as conn:
    # Find companies with missing address or email
    rows = conn.execute(text("""
        SELECT c.company_id, c.legal_name, c.primary_email, sr.raw_payload
        FROM companies c
        LEFT JOIN source_records sr ON sr.source_record_id = c.source_record_id
        WHERE c.is_ankara = TRUE AND c.is_osb_member = TRUE
        AND (
            (sr.raw_payload->>'adres' IS NULL OR sr.raw_payload->>'adres' = '')
            OR (c.primary_email IS NULL OR c.primary_email = '')
        )
    """)).fetchall()

    updated = 0
    for row in rows:
        company_id, legal_name, current_email, raw_payload = row
        key = (legal_name or "").lower().strip()
        
        if key not in aso_lookup:
            continue
        
        aso = aso_lookup[key]
        updates = {}
        
        # Fill address if missing
        if raw_payload is None or (raw_payload.get("adres") if isinstance(raw_payload, dict) else None) is None:
            aso_adres = (aso.get("adres") or "").strip()
            if aso_adres:
                updates["adres"] = aso_adres
        
        # Fill email if missing
        if not current_email:
            aso_email = aso.get("eposta")
            if aso_email:
                updates["email"] = aso_email
        
        if updates:
            # Update source_records payload
            payload = dict(raw_payload) if isinstance(raw_payload, dict) else {}
            if "adres" in updates:
                payload["adres"] = updates["adres"]
            if "email" in updates:
                payload["email"] = updates["email"]
            
            conn.execute(text("""
                UPDATE source_records 
                SET raw_payload = :payload,
                    raw_address = COALESCE(:adres, raw_address),
                    raw_email = COALESCE(:email, raw_email)
                WHERE source_record_id = (
                    SELECT source_record_id FROM companies WHERE company_id = :cid
                )
            """), {
                "payload": json.dumps(payload, ensure_ascii=False),
                "adres": updates.get("adres"),
                "email": updates.get("email"),
                "cid": company_id
            })
            
            # Update companies table
            set_clauses = []
            params = {"cid": company_id}
            if "email" in updates:
                set_clauses.append("primary_email = COALESCE(:email, primary_email)")
                params["email"] = updates["email"]
            
            if set_clauses:
                conn.execute(text(f"""
                    UPDATE companies SET {', '.join(set_clauses)}
                    WHERE company_id = :cid
                """), params)
            
            updated += 1
    
    conn.commit()
    print(f"Güncellenen firma: {updated}")
