# -*- coding: utf-8 -*-
"""P4-4: dashboard/API performans probu - 5 kritik sorgunun EXPLAIN ANALYZE suresi."""
import sys, time
sys.path.insert(0, "src")
from company_master.db.connection import get_engine
from sqlalchemy import text

SORGULAR = {
    "liste_ilk_sayfa": "SELECT * FROM companies ORDER BY data_quality_score DESC LIMIT 20",
    "arama_trgm": "SELECT * FROM companies WHERE legal_name ILIKE '%DOGAN%' LIMIT 20",
    "sayim_toplam": "SELECT COUNT(*) FROM companies",
    "nace_dagilim": "SELECT nace_code, COUNT(*) FROM companies GROUP BY nace_code ORDER BY 2 DESC LIMIT 20",
    "vkn_dolu": "SELECT * FROM companies WHERE tax_number IS NOT NULL AND tax_number != '' LIMIT 20",
}

e = get_engine()
with e.connect() as c:
    for ad, sql in SORGULAR.items():
        t0 = time.perf_counter()
        c.execute(text("EXPLAIN ANALYZE " + sql)).fetchall()
        ms = (time.perf_counter() - t0) * 1000
        print(f"{ad}: {ms:.0f} ms")
