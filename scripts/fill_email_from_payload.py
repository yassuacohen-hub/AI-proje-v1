#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""raw_payload'daki emailler listesinden primary_email doldur."""
import sys, json
sys.path.insert(0, "src")
from company_master.db.connection import get_engine
from sqlalchemy import text

eng = get_engine()
with eng.connect() as conn:
    rows = conn.execute(text("""
        SELECT c.company_id, sr.raw_payload
        FROM companies c
        LEFT JOIN source_records sr ON sr.source_record_id = c.source_record_id
        WHERE c.is_ankara=TRUE AND c.is_osb_member=TRUE
        AND (c.primary_email IS NULL OR c.primary_email = '')
    """)).fetchall()
    
    updated = 0
    for row in rows:
        company_id, raw_payload = row
        if not raw_payload:
            continue
        
        try:
            emailler = raw_payload.get("emailler") if isinstance(raw_payload, dict) else None
            if emailler and len(emailler) > 0:
                email = emailler[0]
                if isinstance(email, dict):
                    email = email.get("adres") or email.get("email") or str(email)
                elif not isinstance(email, str):
                    email = str(email)
                
                conn.execute(text("""
                    UPDATE companies SET primary_email = :email
                    WHERE company_id = :cid
                """), {"email": email, "cid": company_id})
                updated += 1
        except:
            continue
    
    conn.commit()
    print(f"Guncellenen firma: {updated}")
