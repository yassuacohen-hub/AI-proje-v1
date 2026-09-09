#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""DB kalite skorlarini yeniden hesapla - Python ile hesapla, batch update."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sqlalchemy import text
from company_master.db.connection import get_engine

engine = get_engine()

with engine.connect() as conn:
    # Calculate all scores in one query
    rows = conn.execute(text("""
        SELECT c.company_id,
            COALESCE(c.primary_phone, sr.raw_phone) as phone,
            COALESCE(c.primary_email, sr.raw_email) as email,
            COALESCE(c.website_domain, sr.raw_website, c.web_sitesi) as web,
            COALESCE(sr.raw_address, sr.raw_payload->>'adres') as adres,
            COALESCE(c.nace_name, sr.raw_payload->>'sektor') as sektor,
            COALESCE(c.tax_number, c.vergi_no, sr.raw_tax_number) as vkn,
            c.osb_parsel as parsel,
            COALESCE(c.nace_code, sr.raw_nace, sr.raw_payload->>'nace_code') as nace
        FROM companies c
        LEFT JOIN source_records sr ON sr.source_record_id = c.source_record_id
        WHERE c.is_ankara = TRUE AND c.is_osb_member = TRUE
        ORDER BY c.company_id
    """)).fetchall()
    
    print(f"Toplam firma: {len(rows)}")
    
    # Calculate scores in Python
    updates = []
    for row in rows:
        score = 10  # base
        if row.phone:
            score += 10
        if row.email:
            score += 5
        if row.web:
            score += 15
        if row.adres:
            score += 20
        if row.sektor:
            score += 10
        if row.vkn:
            score += 20
        if row.parsel:
            score += 15
        if row.nace:
            score += 5
        score = max(0, min(100, score))
        updates.append((score, row.company_id))
    
    # Batch update using executemany
    print("Guncelleme yapiliyor...")
    with engine.begin() as update_conn:
        update_conn.execute(text("""
            UPDATE companies SET data_quality_score = :score
            WHERE company_id = :cid
        """), [{"score": s, "cid": cid} for s, cid in updates])
    
    avg = conn.execute(text("""
        SELECT AVG(data_quality_score) FROM companies 
        WHERE is_ankara = TRUE AND is_osb_member = TRUE
    """)).scalar()
    
    print(f"Toplam: {len(updates)}, Ortalama: {avg:.2f}")
