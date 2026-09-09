# -*- coding: utf-8 -*-
"""P4-4: EXPLAIN ciktisinda Seq Scan / Index kullanimi detayi."""
import sys
sys.path.insert(0, "src")
from company_master.db.connection import get_engine
from sqlalchemy import text

SORGULAR = {
    "liste_ilk_sayfa": "SELECT * FROM companies ORDER BY data_quality_score DESC LIMIT 20",
    "arama_trgm": "SELECT * FROM companies WHERE legal_name ILIKE '%DOGAN%' LIMIT 20",
    "nace_dagilim": "SELECT nace_code, COUNT(*) FROM companies GROUP BY nace_code ORDER BY 2 DESC LIMIT 20",
}

e = get_engine()
with e.connect() as c:
    for ad, sql in SORGULAR.items():
        print("=" * 20, ad, "=" * 20)
        for (satir,) in c.execute(text("EXPLAIN " + sql)).fetchall():
            print(" ", satir)
    print("=" * 20, "mevcut indexler", "=" * 20)
    for r in c.execute(text(
        "SELECT indexname, indexdef FROM pg_indexes WHERE tablename='companies'"
    )).fetchall():
        print(" ", r[0], "->", r[1][:110])
