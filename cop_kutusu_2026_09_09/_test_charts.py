# -*- coding: utf-8 -*-
"""Yeni grafik SQL'lerini dogrula"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(r"C:\Projeler\Huginn Data Insights") / "src"))
from sqlalchemy import text
from company_master.db.connection import get_engine

engine = get_engine()
where_sql = "WHERE is_ankara = TRUE"

with engine.connect() as conn:
    buckets = conn.execute(text(f"""
        SELECT width_bucket(COALESCE(data_quality_score, 0), 0, 100, 10) AS b,
               COUNT(*) AS adet
        FROM companies {where_sql}
        GROUP BY b ORDER BY b
    """)).fetchall()
print("Histogram OK:", [(int(b), int(n)) for b, n in buckets])

with engine.connect() as conn:
    nace = conn.execute(text(f"""
        SELECT COALESCE(NULLIF(nace_code, ''), 'Bilinmiyor') AS nace,
               COUNT(*) AS adet
        FROM companies {where_sql}
        GROUP BY 1 ORDER BY adet DESC LIMIT 5
    """)).fetchall()
print("NACE OK:", nace)
print("TUM GRAFIK SORGULARI GECTI")
