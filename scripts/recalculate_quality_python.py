#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""DB kalite skorlarini yeniden hesapla - basit UPDATE."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sqlalchemy import text
from company_master.db.connection import get_engine

engine = get_engine()

with engine.connect() as conn:
    # Get all company_ids
    rows = conn.execute(text("""
        SELECT company_id FROM companies 
        WHERE is_ankara = TRUE AND is_osb_member = TRUE
        ORDER BY company_id
    """)).fetchall()
    
    company_ids = [r[0] for r in rows]
    print(f"Toplam firma: {len(company_ids)}")
    
    updated = 0
    for i, company_id in enumerate(company_ids):
        # Calculate score for this company
        score_row = conn.execute(text("""
            SELECT 
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
            WHERE c.company_id = :cid
        """), {"cid": company_id}).first()
        
        if not score_row:
            continue
        
        score = 10  # base
        if score_row.phone:
            score += 10
        if score_row.email:
            score += 5
        if score_row.web:
            score += 15
        if score_row.adres:
            score += 20
        if score_row.sektor:
            score += 10
        if score_row.vkn:
            score += 20
        if score_row.parsel:
            score += 15
        if score_row.nace:
            score += 5
        
        score = max(0, min(100, score))
        
        conn.execute(text("""
            UPDATE companies SET data_quality_score = :score
            WHERE company_id = :cid
        """), {"score": score, "cid": company_id})
        
        updated += 1
        if updated % 100 == 0:
            print(f"Ilerleme: {updated}/{len(company_ids)}")
            conn.commit()
    
    conn.commit()
    
    avg = conn.execute(text("""
        SELECT AVG(data_quality_score) FROM companies 
        WHERE is_ankara = TRUE AND is_osb_member = TRUE
    """)).scalar()
    
    print(f"Toplam: {updated}, Ortalama: {avg:.2f}")
