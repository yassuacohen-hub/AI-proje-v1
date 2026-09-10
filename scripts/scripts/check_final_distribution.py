#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
sys.path.insert(0, "src")
from company_master.db.connection import get_engine
from sqlalchemy import text

eng = get_engine()
with eng.connect() as conn:
    r = conn.execute(text("""
        SELECT 
            COUNT(*) FILTER (WHERE data_quality_score = 0) as zero,
            COUNT(*) FILTER (WHERE data_quality_score > 0 AND data_quality_score < 20) as low,
            COUNT(*) FILTER (WHERE data_quality_score >= 20 AND data_quality_score < 40) as mid,
            COUNT(*) FILTER (WHERE data_quality_score >= 40 AND data_quality_score < 60) as good,
            COUNT(*) FILTER (WHERE data_quality_score >= 60 AND data_quality_score < 80) as better,
            COUNT(*) FILTER (WHERE data_quality_score >= 80) as best,
            AVG(data_quality_score) as avg
        FROM companies
        WHERE is_ankara=TRUE AND is_osb_member=TRUE
    """)).mappings().first()
    
    print("Kalite skoru dagilimi:")
    print(f"  0: {r['zero']}")
    print(f"  1-19: {r['low']}")
    print(f"  20-39: {r['mid']}")
    print(f"  40-59: {r['good']}")
    print(f"  60-79: {r['better']}")
    print(f"  80+: {r['best']}")
    print(f"  Ortalama: {r['avg']:.2f}")
