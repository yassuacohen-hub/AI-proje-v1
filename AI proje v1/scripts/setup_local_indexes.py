# -*- coding: utf-8 -*-
"""Y15: Yerel PostgreSQL index kurulumu + dogrulama.

Kullanim:
    DATABASE_URL=postgresql+psycopg://huginn:huginn_local_dev@localhost:5433/huginn \
        python scripts/setup_local_indexes.py

- pg_trgm extension acar (IF NOT EXISTS)
- Supabase'deki ile ayni arama index'lerini kurar (IF NOT EXISTS)
- join/lookup index'leri ekler (entity_resolution, source_records)
- ILIKE aramayi EXPLAIN ile dogrular
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sqlalchemy import text

from company_master.db.connection import get_engine

INDEXES = [
    # arama (Supabase'de dogrulanmis plan: trigram)
    ("idx_companies_legal_name_trgm", "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_companies_legal_name_trgm ON companies USING gin (legal_name gin_trgm_ops)"),
    ("idx_companies_search_text_trgm", "CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_companies_search_text_trgm ON companies USING gin (search_text gin_trgm_ops)"),
    # lookup/join (restore create-table'larda yok)
    ("idx_er_company_id", "CREATE INDEX IF NOT EXISTS idx_er_company_id ON entity_resolution (company_id)"),
    ("idx_sr_source_id", "CREATE INDEX IF NOT EXISTS idx_sr_source_id ON source_records (source_id)"),
    ("idx_sr_external_id", "CREATE INDEX IF NOT EXISTS idx_sr_external_id ON source_records (external_id)"),
    ("idx_companies_nace", "CREATE INDEX IF NOT EXISTS idx_companies_nace ON companies (nace_code)"),
    ("idx_companies_score", "CREATE INDEX IF NOT EXISTS idx_companies_score ON companies (data_quality_score DESC)"),
]


def main() -> None:
    engine = get_engine()
    print(f"DB: {str(engine.url).split('@')[-1]}")

    with engine.connect() as c:
        # 1) pg_trgm ac (CONCURRENTLY icin degil, extension icin gerekli)
        c.execute(text("CREATE EXTENSION IF NOT EXISTS pg_trgm"))
        c.commit()
        print("+ pg_trgm extension OK")

    # 2) index'ler (CONCURRENTLY olanlar autocommit ile kosulur)
    for name, sql in INDEXES:
        if "CONCURRENTLY" in sql:
            with engine.connect().execution_options(isolation_level="AUTOCOMMIT") as c:
                c.execute(text(sql))
        else:
            with engine.begin() as c:
                c.execute(text(sql))
        print(f"+ {name} OK")

    # 3) EXPLAIN ile dogrula
    with engine.connect() as c:
        raw = c.execute(text(
            "EXPLAIN (FORMAT JSON) SELECT legal_name FROM companies "
            "WHERE legal_name ILIKE :q LIMIT 5"
        ), {"q": "%otomotiv%"}).scalar()
        plan = (raw if isinstance(raw, list) else json.loads(raw))[0]["Plan"]
        print("\n--- EXPLAIN (ILIKE %otomotiv%) ---")
        print("node:", plan["Node Type"], "| index:", plan.get("Index Name", "-"))
        print("total_cost:", plan["Total Cost"], "| est_rows:", plan["Plan Rows"])

    print("\nY15 index kurulumu tamamlandi.")


if __name__ == "__main__":
    main()
